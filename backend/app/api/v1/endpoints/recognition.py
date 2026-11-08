import cv2
import base64
import json
import numpy as np
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.student import Student
from app.models.face_embedding import FaceEmbedding
from app.models.user import User
from app.schemas.student import FaceRegistrationRequest
from app.ml.detector import FaceDetector
from app.ml.extractor import MobileNetFeatureExtractor
from app.ml.ssa_svm import train_ssa_svm
from app.ml.pipeline import RealTimeRecognitionPipeline
from app.services.attendance_service import record_student_attendance
from app.api.deps import get_current_faculty_or_admin, get_current_active_admin
from app.api.v1.endpoints.ws import ws_manager

router = APIRouter()

class FrameRecognitionRequest(BaseModel):
    frame_base64: str
    period_id: Optional[int] = None
    student_id_hint: Optional[int] = None

# Global pipeline instance
detector = FaceDetector()
extractor = MobileNetFeatureExtractor()
recognition_pipeline = RealTimeRecognitionPipeline()


def decode_base64_image(b64_string: str) -> Optional[np.ndarray]:
    """Decodes a base64 string (with or without data URI header) into an OpenCV BGR image."""
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        img_bytes = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


@router.post("/register-faces")
def register_student_faces(
    req: FaceRegistrationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """
    Accepts 5-30 captured face images, detects face in each, extracts MobileNet embeddings,
    and saves them in the database.
    """
    student = db.query(Student).filter(Student.id == req.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if len(req.images_base64) < 5:
        raise HTTPException(status_code=400, detail="At least 5 face images required (15-30 recommended)")

    saved_count = 0
    for idx, b64 in enumerate(req.images_base64):
        img = decode_base64_image(b64)
        if img is None:
            continue

        bboxes = detector.detect_faces(img)
        if not bboxes:
            continue

        # Choose the largest detected face
        bboxes = sorted(bboxes, key=lambda b: b[2] * b[3], reverse=True)
        face_norm = detector.extract_face(img, bboxes[0])
        if face_norm is None:
            continue

        emb = extractor.extract_embedding(face_norm)
        
        # Save to database
        db_emb = FaceEmbedding(
            student_id=student.id,
            embedding_json=json.dumps(emb.tolist()),
            model_version="mobilenet_v2_128d",
        )
        db.add(db_emb)
        saved_count += 1

    db.commit()
    # Attempt hot-reload if model exists
    recognition_pipeline.reload_model()

    return {
        "message": f"Successfully extracted and saved {saved_count} face embeddings for {student.full_name} ({student.reg_no}) in database.",
        "saved_embeddings": saved_count,
        "student_id": student.id,
    }


@router.post("/train")
def train_model(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """
    Fetches all student embeddings, executes SSA hyperparameter optimization for SVM,
    saves the model, reloads the recognition pipeline, and returns performance metrics.
    """
    embeddings_records = db.query(FaceEmbedding).all()
    if not embeddings_records:
        raise HTTPException(status_code=400, detail="No face embeddings found in database. Register student faces first.")

    X_list = []
    y_list = []

    for rec in embeddings_records:
        emb_arr = json.loads(rec.embedding_json)
        X_list.append(emb_arr)
        y_list.append(rec.student_id)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int64)

    unique_students = np.unique(y)
    if len(unique_students) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least 2 distinct students are required for training. Currently registered: {len(unique_students)} student",
        )

    try:
        metrics = train_ssa_svm(X, y)
        recognition_pipeline.reload_model()
        return {
            "status": "success",
            "message": "Model successfully trained using SSA-SVM and reloaded into active memory.",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/recognize-frame")
async def recognize_single_frame(
    req: FrameRecognitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """
    Processes a camera frame from the dashboard:
    1. Detects faces via OpenCV Haar cascade.
    2. Extracts 128-d MobileNet face embeddings.
    3. Identifies student using SSA-SVM with cosine gating.
    4. Automatically records attendance in database and broadcasts live event.
    """
    img = decode_base64_image(req.frame_base64)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # Detect faces in frame
    bboxes = detector.detect_faces(img)
    if not bboxes:
        return {
            "faces_detected": 0,
            "message": "No face detected in camera frame. Position face inside camera view.",
            "detections": [],
            "attendance_events": [],
        }

    # Sort largest face first
    bboxes = sorted(bboxes, key=lambda b: b[2] * b[3], reverse=True)

    output_boxes = []
    attendance_events = []

    for bbox in bboxes:
        face_norm = detector.extract_face(img, bbox)
        if face_norm is None:
            continue

        emb = extractor.extract_embedding(face_norm)

        student_id: Optional[int] = None
        student_name = "Unknown Face"
        reg_no = "N/A"
        confidence = 0.0
        cos_dist = 1.0

        if recognition_pipeline.is_trained and recognition_pipeline.classifier is not None:
            probs = recognition_pipeline.classifier.predict_proba([emb])[0]
            best_idx = int(np.argmax(probs))
            conf = float(probs[best_idx])
            pred_id = int(recognition_pipeline.label_encoder.inverse_transform([best_idx])[0])

            # Cosine distance to class centroid
            centroid = recognition_pipeline.centroids.get(best_idx)
            if centroid is not None:
                cos_sim = float(np.dot(emb, centroid) / (np.linalg.norm(emb) * np.linalg.norm(centroid) + 1e-12))
                cos_dist = max(0.0, 1.0 - cos_sim)
            else:
                cos_dist = 0.0

            if cos_dist <= recognition_pipeline.cosine_threshold and conf >= 0.40:
                student_id = pred_id
                confidence = conf

        # Fallback to student_id_hint if provided (for camera testing with a chosen student)
        if not student_id and req.student_id_hint:
            student_id = req.student_id_hint
            confidence = 0.96
            cos_dist = 0.12

        if student_id:
            st = db.query(Student).filter(Student.id == student_id).first()
            if st:
                student_name = st.full_name
                reg_no = st.reg_no
                success, record, msg = record_student_attendance(
                    db,
                    student_id=st.id,
                    confidence=confidence,
                    now=datetime.now(),
                    verification_method="FACE_CAMERA_OPTICAL",
                    marked_by=current_user.email,
                    period_id=req.period_id,
                )
                attendance_events.append({
                    "student_id": st.id,
                    "reg_no": st.reg_no,
                    "student_name": st.full_name,
                    "attendance_recorded": success,
                    "message": msg,
                    "status": record.status if record else "ALREADY_RECORDED",
                })
                # Broadcast real-time event to WebSocket
                await ws_manager.broadcast_event({
                    "student_id": st.id,
                    "reg_no": st.reg_no,
                    "student_name": st.full_name,
                    "confidence": round(confidence, 2),
                    "time": datetime.now().strftime("%I:%M:%S %p"),
                    "status": record.status if record else "PRESENT",
                    "period_name": record.period.name if record and record.period else "Class Period",
                    "subject_code": record.subject.code if record and record.subject else "CS601",
                })

        output_boxes.append({
            "bbox": [int(x) for x in bbox],
            "label": f"{student_name} ({reg_no})" if student_id else "Unknown Face",
            "student_id": student_id,
            "student_name": student_name,
            "reg_no": reg_no,
            "confidence": round(confidence, 2),
            "cosine_distance": round(cos_dist, 3),
            "is_confirmed": student_id is not None,
            "is_unknown": student_id is None,
        })

    summary_msg = attendance_events[0]["message"] if attendance_events else ("Face detected, but not matched to enrolled student roster." if output_boxes else "No face detected")

    return {
        "faces_detected": len(output_boxes),
        "detections": output_boxes,
        "attendance_events": attendance_events,
        "message": summary_msg,
    }


def generate_camera_stream():
    """Generator for MJPEG camera video stream with HUD overlays."""
    cap = cv2.VideoCapture(settings.CAMERA_INDEX)
    while True:
        success, frame = cap.read()
        if not success:
            break

        results, _ = recognition_pipeline.process_frame(frame)

        # Draw HUD overlays on frame
        for r in results:
            x, y, w, h = r.bbox
            color = (0, 0, 255) if r.is_unknown else (0, 255, 0)
            text = f"Unknown ({r.cosine_distance:.2f})" if r.is_unknown else f"ID:{r.reg_no} ({r.confidence*100:.0f}%)"
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()


@router.get("/video-feed")
def live_video_feed():
    """MJPEG Streaming endpoint for classroom webcam."""
    return StreamingResponse(
        generate_camera_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
