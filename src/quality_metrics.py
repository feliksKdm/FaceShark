"""Image quality assessment metrics."""
import cv2
import numpy as np
from typing import Dict, Tuple, List


class QualityMetrics:
    """Calculate image quality metrics."""
    
    @staticmethod
    def calculate_sharpness_laplacian(image: np.ndarray) -> float:
        """Calculate Laplacian variance sharpness."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(np.var(laplacian))
    
    @staticmethod
    def calculate_sharpness_tenengrad(image: np.ndarray) -> float:
        """Calculate Tenengrad sharpness."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        tenengrad = np.sum(gx**2 + gy**2)
        return float(tenengrad)
    
    @staticmethod
    def calculate_sharpness_fft(image: np.ndarray) -> float:
        """Calculate FFT high-frequency ratio."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)
        
        h, w = gray.shape
        center_x, center_y = w // 2, h // 2
        radius = min(h, w) // 4
        
        # High frequency mask (outer region)
        y, x = np.ogrid[:h, :w]
        mask = (x - center_x)**2 + (y - center_y)**2 > radius**2
        
        high_freq_energy = np.sum(magnitude[mask])
        total_energy = np.sum(magnitude)
        
        return float(high_freq_energy / total_energy) if total_energy > 0 else 0.0
    
    @staticmethod
    def calculate_contrast_rms(image: np.ndarray) -> float:
        """Calculate RMS contrast."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_intensity = np.mean(gray)
        if mean_intensity == 0:
            return 0.0
        variance = np.mean((gray - mean_intensity) ** 2)
        rms = np.sqrt(variance)
        return float(rms / mean_intensity * 100)  # Normalized percentage
    
    @staticmethod
    def calculate_exposure(image: np.ndarray) -> Dict[str, float]:
        """Calculate exposure metrics."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        mean_brightness = np.mean(gray)
        
        # Ideal exposure around 128 (middle gray)
        exposure_score = 100 - abs(mean_brightness - 128) / 128 * 100
        
        # Check for over/under exposure
        overexposed = np.sum(gray > 240) / gray.size * 100
        underexposed = np.sum(gray < 15) / gray.size * 100
        
        return {
            'score': float(max(0, min(100, exposure_score))),
            'mean_brightness': float(mean_brightness),
            'overexposed_pct': float(overexposed),
            'underexposed_pct': float(underexposed),
            'exposure_diff': float(mean_brightness - 128)
        }
    
    @staticmethod
    def calculate_local_sharpness_map(image: np.ndarray, kernel_size: int = 9) -> np.ndarray:
        """Calculate local sharpness map."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=kernel_size)
        sharpness_map = np.abs(laplacian)
        return sharpness_map
    
    @staticmethod
    def calculate_noise_estimate(image: np.ndarray) -> float:
        """Estimate noise level using standard deviation of smooth regions."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        # Apply Gaussian blur to get smooth regions
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        diff = gray.astype(np.float32) - blurred.astype(np.float32)
        noise_std = np.std(diff)
        return float(noise_std)
    
    @staticmethod
    def calculate_background_bokeh(image: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> float:
        """Estimate background blur (bokeh effect)."""
        x, y, w, h = face_bbox
        h_img, w_img = image.shape[:2]
        
        # Extract face region
        face_region = image[max(0, y):min(h_img, y+h), max(0, x):min(w_img, x+w)]
        
        # Create mask excluding face region
        mask = np.ones((h_img, w_img), dtype=np.uint8) * 255
        mask[max(0, y):min(h_img, y+h), max(0, x):min(w_img, x+w)] = 0
        
        # Calculate sharpness in background vs face
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        face_sharpness = QualityMetrics.calculate_sharpness_laplacian(face_region)
        
        background_mask = mask > 0
        if np.any(background_mask):
            background_region = gray[background_mask]
            bg_sharpness = QualityMetrics.calculate_sharpness_laplacian(
                background_region.reshape(-1, 1)
            )
            
            # Higher ratio = more bokeh (background is blurrier)
            if face_sharpness > 0:
                bokeh_ratio = bg_sharpness / face_sharpness
                # Normalize to 0-100 scale
                bokeh_score = min(100, max(0, (1 - bokeh_ratio) * 100))
                return float(bokeh_score)
        
        return 50.0  # Default if can't calculate
    
    @staticmethod
    def get_all_metrics(image: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> Dict:
        """Get all quality metrics."""
        return {
            'sharpness_laplacian': QualityMetrics.calculate_sharpness_laplacian(image),
            'sharpness_tenengrad': QualityMetrics.calculate_sharpness_tenengrad(image),
            'sharpness_fft': QualityMetrics.calculate_sharpness_fft(image),
            'contrast_rms': QualityMetrics.calculate_contrast_rms(image),
            'exposure': QualityMetrics.calculate_exposure(image),
            'noise': QualityMetrics.calculate_noise_estimate(image),
            'bokeh': QualityMetrics.calculate_background_bokeh(image, face_bbox),
            'sharpness_map': QualityMetrics.calculate_local_sharpness_map(image).tolist()
        }

