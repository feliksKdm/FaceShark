"""Face geometry analysis: pose, jawline, proportions."""
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class FacePose:
    """Face pose angles."""
    yaw: float  # Left-right rotation
    pitch: float  # Up-down rotation
    roll: float  # Tilt rotation


@dataclass
class FaceProportions:
    """Face proportions and measurements."""
    jaw_angle: float  # Angle of jawline
    eye_distance: float
    face_width: float
    face_height: float
    symmetry_score: float
    cheekbone_prominence: float


class GeometryAnalyzer:
    """Analyze face geometry and pose."""
    
    # MediaPipe Face Mesh landmark indices
    # Key facial points
    LEFT_EYE_OUTER = 33
    LEFT_EYE_INNER = 133
    RIGHT_EYE_OUTER = 263
    RIGHT_EYE_INNER = 362
    NOSE_TIP = 4
    LEFT_MOUTH = 61
    RIGHT_MOUTH = 291
    CHIN = 152
    LEFT_JAW = 172
    RIGHT_JAW = 397
    LEFT_CHEEKBONE = 116
    RIGHT_CHEEKBONE = 345
    
    def __init__(self):
        pass
    
    def calculate_pose(self, landmarks_468: np.ndarray) -> FacePose:
        """Calculate face pose (yaw, pitch, roll) from 468 landmarks."""
        if landmarks_468 is None or len(landmarks_468) < 468:
            return FacePose(0.0, 0.0, 0.0)
        
        # Get key points
        left_eye = landmarks_468[self.LEFT_EYE_OUTER]
        right_eye = landmarks_468[self.RIGHT_EYE_OUTER]
        nose_tip = landmarks_468[self.NOSE_TIP]
        chin = landmarks_468[self.CHIN]
        
        # Calculate roll (tilt)
        eye_vec = right_eye[:2] - left_eye[:2]
        roll = np.arctan2(eye_vec[1], eye_vec[0]) * 180 / np.pi
        
        # Calculate pitch (vertical rotation)
        # Use nose tip and chin vertical distance
        vertical_vec = chin[:2] - nose_tip[:2]
        pitch = np.arctan2(vertical_vec[1], np.linalg.norm(vertical_vec)) * 180 / np.pi
        
        # Calculate yaw (horizontal rotation)
        # Use eye positions and nose tip
        eye_center = (left_eye[:2] + right_eye[:2]) / 2
        nose_to_eye = nose_tip[:2] - eye_center
        eye_width = np.linalg.norm(eye_vec)
        
        # Approximate yaw from nose position relative to eye center
        yaw = np.arctan2(nose_to_eye[0], eye_width / 2) * 180 / np.pi
        
        return FacePose(
            yaw=float(yaw),
            pitch=float(pitch),
            roll=float(roll)
        )
    
    def calculate_jaw_angle(self, landmarks_468: np.ndarray) -> float:
        """Calculate jawline angle."""
        if landmarks_468 is None or len(landmarks_468) < 468:
            return 90.0  # Default right angle
        
        left_jaw = landmarks_468[self.LEFT_JAW]
        right_jaw = landmarks_468[self.RIGHT_JAW]
        chin = landmarks_468[self.CHIN]
        
        # Calculate angle at chin
        vec1 = left_jaw[:2] - chin[:2]
        vec2 = right_jaw[:2] - chin[:2]
        
        cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        cos_angle = np.clip(cos_angle, -1, 1)
        angle = np.arccos(cos_angle) * 180 / np.pi
        
        return float(angle)
    
    def calculate_proportions(self, landmarks_468: np.ndarray) -> FaceProportions:
        """Calculate face proportions."""
        if landmarks_468 is None or len(landmarks_468) < 468:
            return FaceProportions(
                jaw_angle=90.0,
                eye_distance=0.0,
                face_width=0.0,
                face_height=0.0,
                symmetry_score=0.0,
                cheekbone_prominence=0.0
            )
        
        # Eye distance
        left_eye = landmarks_468[self.LEFT_EYE_OUTER]
        right_eye = landmarks_468[self.RIGHT_EYE_OUTER]
        eye_distance = np.linalg.norm(right_eye[:2] - left_eye[:2])
        
        # Face dimensions
        left_side = landmarks_468[self.LEFT_JAW]
        right_side = landmarks_468[self.RIGHT_JAW]
        face_width = np.linalg.norm(right_side[:2] - left_side[:2])
        
        forehead = landmarks_468[10]  # Approximate forehead point
        chin = landmarks_468[self.CHIN]
        face_height = np.linalg.norm(chin[:2] - forehead[:2])
        
        # Jaw angle
        jaw_angle = self.calculate_jaw_angle(landmarks_468)
        
        # Symmetry score (left-right symmetry)
        left_points = landmarks_468[[self.LEFT_EYE_OUTER, self.LEFT_JAW, self.LEFT_MOUTH, self.LEFT_CHEEKBONE]]
        right_points = landmarks_468[[self.RIGHT_EYE_OUTER, self.RIGHT_JAW, self.RIGHT_MOUTH, self.RIGHT_CHEEKBONE]]
        
        # Mirror right points and compare
        face_center_x = (left_side[0] + right_side[0]) / 2
        right_points_mirrored = right_points.copy()
        right_points_mirrored[:, 0] = 2 * face_center_x - right_points_mirrored[:, 0]
        
        # Calculate average distance
        distances = [
            np.linalg.norm(left_points[i][:2] - right_points_mirrored[i][:2])
            for i in range(len(left_points))
        ]
        avg_distance = np.mean(distances)
        max_distance = face_width
        symmetry_score = max(0, 100 - (avg_distance / max_distance * 100)) if max_distance > 0 else 0
        
        # Cheekbone prominence (distance from cheekbone to face edge)
        left_cheek = landmarks_468[self.LEFT_CHEEKBONE]
        right_cheek = landmarks_468[self.RIGHT_CHEEKBONE]
        cheek_width = np.linalg.norm(right_cheek[:2] - left_cheek[:2])
        cheekbone_prominence = (cheek_width / face_width * 100) if face_width > 0 else 0
        
        return FaceProportions(
            jaw_angle=float(jaw_angle),
            eye_distance=float(eye_distance),
            face_width=float(face_width),
            face_height=float(face_height),
            symmetry_score=float(symmetry_score),
            cheekbone_prominence=float(cheekbone_prominence)
        )
    
    def detect_occlusions(self, landmarks_468: np.ndarray, image_shape: Tuple[int, int]) -> Dict[str, bool]:
        """Detect occlusions (glasses, mask, hand)."""
        # Simplified occlusion detection
        # In production, would use more sophisticated methods
        occlusions = {
            'glasses': False,
            'mask': False,
            'hand': False
        }
        
        # Check for glasses (distance between eye and eyebrow)
        # Check for mask (mouth region coverage)
        # Check for hand (skin color detection in front of face)
        
        return occlusions
    
    def calculate_pose_score(self, pose: FacePose) -> float:
        """Calculate pose quality score (0-100)."""
        # Ideal: yaw=0, pitch=0, roll=0
        yaw_score = max(0, 100 - abs(pose.yaw) * 2)
        pitch_score = max(0, 100 - abs(pose.pitch) * 2)
        roll_score = max(0, 100 - abs(pose.roll) * 2)
        
        # Weighted average
        pose_score = (yaw_score * 0.4 + pitch_score * 0.4 + roll_score * 0.2)
        return float(pose_score)
    
    def calculate_jawline_score(self, jaw_angle: float, proportions: FaceProportions) -> float:
        """Calculate jawline quality score (0-100)."""
        # Ideal jaw angle around 60-80 degrees
        ideal_angle = 70
        angle_diff = abs(jaw_angle - ideal_angle)
        angle_score = max(0, 100 - angle_diff * 2)
        
        # Combine with symmetry
        jawline_score = (angle_score * 0.6 + proportions.symmetry_score * 0.4)
        return float(jawline_score)

