import cv2
import base64
import json
import numpy as np
from typing import List, Optional
from datetime import datetime
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

router = APIRouter()

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
    admin: User = Depends(get_current_active_admin),
):
    """
    Accepts 15-30 captured face images, detects face in each, extracts MobileNet embeddings,
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
    return {
        "message": f"Successfully extracted and saved {saved_count} face embeddings for {student.full_name} ({student.reg_no})",
        "saved_embeddings": saved_count,
        "student_id": student.id,
    }


@router.post("/train")
def train_model(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin),
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
            "message": "Model successfully trained using SSA-SVM and reloaded",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/recognize-frame")
def recognize_single_frame(
    frame_base64: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    """
    Processes a single frame sent from the web dashboard webcam feed.
    Detects faces, runs SSA-SVM with cosine gating, marks attendance on confirmed detections.
    """
    img = decode_base64_image(frame_base64)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    results, confirmed_ids = recognition_pipeline.process_frame(img)

    attendance_events = []
    for sid in confirmed_ids:
        st = db.query(Student).filter(Student.id == sid).first()
        if st:
            success, record, msg = record_student_attendance(
                db,
                student_id=sid,
                confidence=0.95,
                now=datetime.now(),
            )
            attendance_events.append({
                "student_id": sid,
                "reg_no": st.reg_no,
                "student_name": st.full_name,
                "attendance_recorded": success,
                "message": msg,
            })

    output_boxes = []
    for r in results:
        label = "Unknown"
        if r.student_id:
            st = db.query(Student).filter(Student.id == r.student_id).first()
            if st:
                label = f"{st.full_name} ({st.reg_no})"

        output_boxes.append({
            "bbox": r.bbox,
            "label": label,
            "confidence": round(r.confidence, 2),
            "cosine_distance": round(r.cosine_distance, 3),
            "is_confirmed": r.is_confirmed,
            "is_unknown": r.is_unknown,
        })

    return {
        "faces_detected": len(output_boxes),
        "detections": output_boxes,
        "attendance_events": attendance_events,
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
