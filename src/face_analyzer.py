"""Main face analysis orchestrator."""
import cv2
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from .face_detection import FaceDetector, FaceLandmarks
from .quality_metrics import QualityMetrics
from .geometry_analysis import GeometryAnalyzer, FacePose, FaceProportions
from .meme_classifier import MemeClassifier


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    ok: bool
    axes: Dict[str, float]
    label: str
    confidence: float
    reasons: List[str]
    abstain: bool
    model_version: str
    pose: Optional[Dict[str, float]] = None
    proportions: Optional[Dict[str, float]] = None
    quality_metrics: Optional[Dict] = None


class FaceAnalyzer:
    """Main face analysis orchestrator."""
    
    def __init__(self, model_version: str = "1.0.0"):
        self.face_detector = FaceDetector()
        self.quality_metrics = QualityMetrics()
        self.geometry_analyzer = GeometryAnalyzer()
        self.meme_classifier = MemeClassifier()
        self.model_version = model_version
    
    def analyze(self, image_path: str) -> AnalysisResult:
        """Analyze face in image."""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return AnalysisResult(
                ok=False,
                axes={},
                label="meh",
                confidence=0.0,
                reasons=["не удалось загрузить изображение"],
                abstain=True,
                model_version=self.model_version
            )
        
        return self.analyze_image(image)
    
    def analyze_image(self, image: np.ndarray) -> AnalysisResult:
        """Analyze face in numpy image array."""
        # Detect face
        landmarks = self.face_detector.detect_and_align(image)
        
        if landmarks is None:
            return AnalysisResult(
                ok=False,
                axes={},
                label="meh",
                confidence=0.0,
                reasons=["лицо не обнаружено"],
                abstain=True,
                model_version=self.model_version
            )
        
        # Extract face region
        x, y, w, h = landmarks.face_bbox
        face_region = image[max(0, y):y+h, max(0, x):x+w]
        
        if face_region.size == 0:
            return AnalysisResult(
                ok=False,
                axes={},
                label="meh",
                confidence=0.0,
                reasons=["не удалось извлечь область лица"],
                abstain=True,
                model_version=self.model_version
            )
        
        # Calculate quality metrics
        quality = self.quality_metrics.get_all_metrics(face_region, (0, 0, w, h))
        
        # Calculate geometry
        pose = None
        proportions = None
        if landmarks.landmarks_468 is not None:
            pose = self.geometry_analyzer.calculate_pose(landmarks.landmarks_468)
            proportions = self.geometry_analyzer.calculate_proportions(landmarks.landmarks_468)
        
        # Calculate axes scores (0-100)
        axes = self._calculate_axes(quality, pose, proportions, landmarks)
        
        # Check if should abstain
        abstain = self._should_abstain(axes, landmarks.confidence, pose)
        
        # Classify meme label
        label, confidence, reasons = self.meme_classifier.classify(axes)
        
        # Build reasons list
        full_reasons = self._build_reasons(axes, quality, pose, proportions, reasons)
        
        # Convert pose and proportions to dicts for JSON serialization
        pose_dict = asdict(pose) if pose else None
        proportions_dict = asdict(proportions) if proportions else None
        
        return AnalysisResult(
            ok=True,
            axes=axes,
            label=label,
            confidence=confidence,
            reasons=full_reasons,
            abstain=abstain,
            model_version=self.model_version,
            pose=pose_dict,
            proportions=proportions_dict,
            quality_metrics=quality
        )
    
    def _calculate_axes(self, quality: Dict, pose: Optional[FacePose], 
                        proportions: Optional[FaceProportions],
                        landmarks: FaceLandmarks) -> Dict[str, float]:
        """Calculate axis scores (0-100)."""
        # Sharpness axis (0-100)
        # Combine multiple sharpness metrics
        laplacian = quality.get('sharpness_laplacian', 0)
        tenengrad = quality.get('sharpness_tenengrad', 0)
        fft = quality.get('sharpness_fft', 0)
        
        # Normalize and combine
        # Rough normalization (would need calibration in production)
        sharpness_score = min(100, (laplacian / 1000 * 50) + (tenengrad / 100000 * 30) + (fft * 20))
        
        # Lighting axis
        exposure = quality.get('exposure', {})
        exposure_score = exposure.get('score', 50)
        lighting_score = exposure_score * 0.7 + (100 - exposure.get('overexposed_pct', 0) - exposure.get('underexposed_pct', 0)) * 0.3
        
        # Pose axis
        if pose:
            pose_score = self.geometry_analyzer.calculate_pose_score(pose)
        else:
            pose_score = 50.0
        
        # Jawline axis
        if proportions:
            jawline_score = self.geometry_analyzer.calculate_jawline_score(
                proportions.jaw_angle, proportions
            )
        else:
            jawline_score = 50.0
        
        # Contrast axis
        contrast_rms = quality.get('contrast_rms', 0)
        contrast_score = min(100, contrast_rms * 2)  # Normalize to 0-100
        
        return {
            'sharpness': float(sharpness_score),
            'lighting': float(lighting_score),
            'pose': float(pose_score),
            'jawline': float(jawline_score),
            'contrast': float(contrast_score)
        }
    
    def _should_abstain(self, axes: Dict[str, float], confidence: float, 
                       pose: Optional[FacePose]) -> bool:
        """Determine if should abstain from classification."""
        # Abstain if confidence too low
        if confidence < 0.3:
            return True
        
        # Abstain if pose too extreme
        if pose:
            if abs(pose.yaw) > 45 or abs(pose.pitch) > 45:
                return True
        
        # Abstain if all axes very low
        avg_score = sum(axes.values()) / len(axes)
        if avg_score < 20:
            return True
        
        return False
    
    def _build_reasons(self, axes: Dict[str, float], quality: Dict,
                      pose: Optional[FacePose], proportions: Optional[FaceProportions],
                      base_reasons: List[str]) -> List[str]:
        """Build detailed reasons list."""
        reasons = base_reasons.copy()
        
        # Add specific technical reasons
        if pose:
            if abs(pose.yaw) > 15:
                reasons.append(f"поворот головы в сторону (yaw≈{pose.yaw:.1f}°)")
            if abs(pose.pitch) > 15:
                reasons.append(f"наклон головы (pitch≈{pose.pitch:.1f}°)")
        
        exposure = quality.get('exposure', {})
        exposure_diff = exposure.get('exposure_diff', 0)
        if abs(exposure_diff) > 10:
            sign = "+" if exposure_diff > 0 else ""
            reasons.append(f"экспозиция {sign}{exposure_diff:.0f}")
        
        if proportions:
            if proportions.symmetry_score < 70:
                reasons.append("низкая симметрия лица")
        
        return reasons
    
    def cleanup(self):
        """Cleanup resources."""
        self.face_detector.cleanup()

