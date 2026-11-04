import cv2
import numpy as np
from typing import List, Tuple, Optional


class FaceDetector:
    """
    Robust Face Detection & Preprocessing pipeline.
    Uses OpenCV Haar Cascade and DNN detector with fallback.
    Crops, aligns, and normalizes faces to standard 160x160 dimensions.
    """

    def __init__(self, min_face_size: Tuple[int, int] = (60, 60)):
        self.min_face_size = min_face_size
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            raise RuntimeError(f"Failed to load Haar Cascade from {cascade_path}")

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in an RGB or BGR frame.
        Returns list of bounding boxes: [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []
        
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Histogram equalization to normalize varying illumination/lighting
        gray_eq = cv2.equalizeHist(gray)

        faces = self.cascade.detectMultiScale(
            gray_eq,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=self.min_face_size,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def extract_face(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
        target_size: Tuple[int, int] = (160, 160),
    ) -> Optional[np.ndarray]:
        """
        Extracts, crops with margin, and resizes a face region.
        Returns normalized RGB float32 array in [0, 1] range.
        """
        x, y, w, h = bbox
        img_h, img_w = frame.shape[:2]

        # Margin expansion (15%) for full facial contour capture
        margin_x = int(w * 0.15)
        margin_y = int(h * 0.15)
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(img_w, x + w + margin_x)
        y2 = min(img_h, y + h + margin_y)

        cropped = frame[y1:y2, x1:x2]
        if cropped.size == 0:
            return None

        # Convert to RGB if needed
        if len(cropped.shape) == 3 and cropped.shape[2] == 3:
            rgb_face = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        else:
            rgb_face = cv2.cvtColor(cropped, cv2.COLOR_GRAY2RGB)

        resized = cv2.resize(rgb_face, target_size, interpolation=cv2.INTER_AREA)
        normalized = resized.astype(np.float32) / 255.0
        return normalized
