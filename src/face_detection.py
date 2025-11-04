"""Face detection and alignment using MediaPipe."""
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class FaceLandmarks:
    """Face landmarks data structure."""
    face_bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    landmarks_5: np.ndarray  # 5 key points for alignment (eyes, nose, mouth)
    landmarks_468: Optional[np.ndarray] = None  # Full face mesh
    confidence: float = 0.0


class FaceDetector:
    """Face detector using MediaPipe Face Detection."""
    
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # Full range model
            min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
    
    def detect_and_align(self, image: np.ndarray) -> Optional[FaceLandmarks]:
        """Detect face and extract landmarks."""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Face detection
        detection_results = self.face_detection.process(rgb_image)
        
        if not detection_results.detections or len(detection_results.detections) == 0:
            return None
        
        detection = detection_results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        
        h, w = image.shape[:2]
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        # Extract 5-point landmarks for alignment
        landmarks_5 = []
        for landmark in detection.location_data.relative_keypoints:
            px = int(landmark.x * w)
            py = int(landmark.y * h)
            landmarks_5.append([px, py])
        landmarks_5 = np.array(landmarks_5, dtype=np.float32)
        
        # Get full face mesh
        mesh_results = self.face_mesh.process(rgb_image)
        landmarks_468 = None
        if mesh_results.multi_face_landmarks:
            face_landmarks = mesh_results.multi_face_landmarks[0]
            landmarks_468 = np.array([
                [lm.x * w, lm.y * h, lm.z * w]
                for lm in face_landmarks.landmark
            ], dtype=np.float32)
        
        return FaceLandmarks(
            face_bbox=(x, y, width, height),
            landmarks_5=landmarks_5,
            landmarks_468=landmarks_468,
            confidence=detection.score[0] if detection.score else 0.0
        )
    
    def align_face(self, image: np.ndarray, landmarks_5: np.ndarray, 
                   output_size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """Align face using similarity transform."""
        # Standard positions for 5-point alignment
        # Left eye, right eye, nose tip, left mouth corner, right mouth corner
        dst_points = np.array([
            [85, 85],   # Left eye
            [171, 85],  # Right eye
            [128, 128], # Nose tip
            [98, 160],  # Left mouth corner
            [158, 160]  # Right mouth corner
        ], dtype=np.float32)
        
        # Scale to output size
        scale = output_size[0] / 256.0
        dst_points = dst_points * scale
        
        # Calculate similarity transform
        transform = cv2.getAffineTransform(
            landmarks_5[:3],  # Use eyes and nose
            dst_points[:3]
        )
        
        aligned = cv2.warpAffine(image, transform, output_size)
        return aligned
    
    def cleanup(self):
        """Cleanup resources."""
        self.face_detection.close()
        self.face_mesh.close()

