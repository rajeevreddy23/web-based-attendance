import os
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from app.ml.detector import FaceDetector
from app.ml.extractor import MobileNetFeatureExtractor
from app.core.config import settings

logger = logging.getLogger(__name__)


class RecognitionResult:
    def __init__(
        self,
        bbox: Tuple[int, int, int, int],
        student_id: Optional[int],
        reg_no: Optional[str],
        confidence: float,
        cosine_distance: float,
        is_confirmed: bool = False,
    ):
        self.bbox = bbox
        self.student_id = student_id
        self.reg_no = reg_no
        self.confidence = confidence
        self.cosine_distance = cosine_distance
        self.is_confirmed = is_confirmed

    @property
    def is_unknown(self) -> bool:
        return self.student_id is None


class RealTimeRecognitionPipeline:
    """
    End-to-end Real-Time Face Recognition Pipeline.
    Combines Face Detection + MobileNet Embeddings + Cosine Distance Threshold Gating +
    SSA-Tuned SVM Classification + Temporal Multi-Frame Streak Confirmation.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        cosine_threshold: Optional[float] = None,
        consecutive_required: Optional[int] = None,
        frame_skip: Optional[int] = None,
    ):
        self.detector = FaceDetector()
        self.extractor = MobileNetFeatureExtractor()
        
        self.model_path = model_path or os.path.join(settings.MODELS_DIR, "ssa_svm_model.pkl")
        self.cosine_threshold = cosine_threshold if cosine_threshold is not None else settings.COSINE_DISTANCE_THRESHOLD
        self.consecutive_required = consecutive_required or settings.CONSECUTIVE_FRAMES_REQUIRED
        self.frame_skip = frame_skip or settings.PROCESS_EVERY_N_FRAMES

        self.classifier = None
        self.label_encoder = None
        self.centroids = {}
        self.is_trained = False

        self.frame_counter = 0
        self.consecutive_tracker: Dict[int, int] = {}
        self.last_results: List[RecognitionResult] = []

        self.reload_model()

    def reload_model(self) -> bool:
        """Loads or reloads the trained SSA-SVM model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    bundle = pickle.load(f)
                    self.classifier = bundle["classifier"]
                    self.label_encoder = bundle["label_encoder"]
                    self.centroids = bundle.get("centroids", {})
                    self.is_trained = True
                    logger.info(f"Loaded trained SSA-SVM model with {len(self.label_encoder.classes_)} classes")
                    return True
            except Exception as e:
                logger.error(f"Error loading model from {self.model_path}: {e}")
        self.is_trained = False
        return False

    def process_frame(self, frame: np.ndarray) -> Tuple[List[RecognitionResult], List[int]]:
        """
        Processes a video frame.
        Returns:
            (all_detections, newly_confirmed_student_ids)
        """
        self.frame_counter += 1

        # Frame skip for real-time throughput
        if (self.frame_counter % self.frame_skip) != 0:
            return self.last_results, []

        bboxes = self.detector.detect_faces(frame)
        if not bboxes:
            # Decay streak counts if no faces detected
            self.consecutive_tracker.clear()
            self.last_results = []
            return [], []

        results = []
        confirmed_students = []
        seen_in_this_frame = set()

        for bbox in bboxes:
            face_norm = self.detector.extract_face(frame, bbox)
            if face_norm is None:
                continue

            emb = self.extractor.extract_embedding(face_norm)

            if not self.is_trained or self.classifier is None:
                results.append(RecognitionResult(bbox, None, "Untrained", 0.0, 1.0))
                continue

            # SVM Probability prediction
            probs = self.classifier.predict_proba([emb])[0]
            best_idx = int(np.argmax(probs))
            confidence = float(probs[best_idx])
            raw_label = self.label_encoder.inverse_transform([best_idx])[0]
            student_id = int(raw_label)

            # Cosine distance gating to class centroid
            centroid = self.centroids.get(best_idx)
            if centroid is not None:
                # Cosine distance = 1 - (u . v)
                cos_sim = float(np.dot(emb, centroid) / (np.linalg.norm(emb) * np.linalg.norm(centroid) + 1e-12))
                cos_dist = max(0.0, 1.0 - cos_sim)
            else:
                cos_dist = 0.0

            # Gating Rule: Reject if distance > threshold or low confidence
            if cos_dist > self.cosine_threshold or confidence < 0.50:
                results.append(RecognitionResult(bbox, None, "Unknown", confidence, cos_dist, is_confirmed=False))
                continue

            seen_in_this_frame.add(student_id)

            # Consecutive streak increment
            current_streak = self.consecutive_tracker.get(student_id, 0) + 1
            self.consecutive_tracker[student_id] = current_streak

            is_confirmed = False
            if current_streak >= self.consecutive_required:
                is_confirmed = True
                confirmed_students.append(student_id)
                # Reset streak counter to require another confirmation cycle
                self.consecutive_tracker[student_id] = 0

            results.append(
                RecognitionResult(
                    bbox=bbox,
                    student_id=student_id,
                    reg_no=str(student_id),
                    confidence=confidence,
                    cosine_distance=cos_dist,
                    is_confirmed=is_confirmed,
                )
            )

        # Decay students not seen in current frame
        for sid in list(self.consecutive_tracker.keys()):
            if sid not in seen_in_this_frame:
                self.consecutive_tracker[sid] = max(0, self.consecutive_tracker[sid] - 1)

        self.last_results = results
        return results, confirmed_students
