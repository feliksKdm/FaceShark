"""Meme classifier: mogged / sigma / meh."""
import numpy as np
from typing import Dict, List, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle


class MemeClassifier:
    """Classify faces into meme categories: mogged, sigma, meh."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.labels = ['mogged', 'sigma', 'meh']
        self._initialize_rule_based()
    
    def _initialize_rule_based(self):
        """Initialize with rule-based classifier (can be replaced with ML later)."""
        self.model_type = 'rule_based'
    
    def classify_rule_based(self, axes: Dict[str, float]) -> Tuple[str, float, List[str]]:
        """Rule-based classification based on axes."""
        sharpness = axes.get('sharpness', 50)
        lighting = axes.get('lighting', 50)
        pose = axes.get('pose', 50)
        jawline = axes.get('jawline', 50)
        contrast = axes.get('contrast', 50)
        
        # Calculate composite score
        composite = (sharpness * 0.25 + lighting * 0.20 + pose * 0.20 + 
                    jawline * 0.20 + contrast * 0.15)
        
        # Determine reasons
        reasons = []
        positive_reasons = []
        negative_reasons = []
        
        if sharpness > 75:
            positive_reasons.append("отличная резкость")
        elif sharpness < 50:
            negative_reasons.append("низкая резкость")
        
        if lighting > 70:
            positive_reasons.append("хорошее освещение")
        elif lighting < 50:
            negative_reasons.append("недостаточное освещение")
        
        if pose > 80:
            positive_reasons.append("идеальная поза")
        elif pose < 60:
            negative_reasons.append("неоптимальная поза")
        
        if jawline > 75:
            positive_reasons.append("чёткая линия челюсти")
        elif jawline < 50:
            negative_reasons.append("нечёткая линия челюсти")
        
        reasons = positive_reasons + negative_reasons
        
        # Classification rules
        if composite >= 80 and sharpness >= 75 and jawline >= 70:
            label = 'mogged'
            confidence = min(0.95, 0.7 + (composite - 80) / 20 * 0.25)
        elif composite >= 65 and (sharpness >= 65 or jawline >= 65):
            label = 'sigma'
            confidence = min(0.9, 0.6 + (composite - 65) / 15 * 0.3)
        else:
            label = 'meh'
            confidence = min(0.85, 0.5 + max(0, (50 - composite) / 50 * 0.35))
        
        return label, float(confidence), reasons
    
    def classify(self, axes: Dict[str, float], embedding: np.ndarray = None) -> Tuple[str, float, List[str]]:
        """Classify face into meme category."""
        if self.model_type == 'rule_based':
            return self.classify_rule_based(axes)
        else:
            # ML-based classification (for future use)
            return self.classify_ml(axes, embedding)
    
    def classify_ml(self, axes: Dict[str, float], embedding: np.ndarray) -> Tuple[str, float, List[str]]:
        """ML-based classification (placeholder for future implementation)."""
        # This would use trained model with embeddings
        # For now, fall back to rule-based
        return self.classify_rule_based(axes)
    
    def train(self, features: np.ndarray, labels: np.ndarray):
        """Train ML classifier (for future use)."""
        features_scaled = self.scaler.fit_transform(features)
        self.model = LogisticRegression(multi_class='multinomial', max_iter=1000)
        self.model.fit(features_scaled, labels)
        self.model_type = 'ml'
    
    def save_model(self, path: str):
        """Save trained model."""
        if self.model:
            with open(path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'labels': self.labels
                }, f)
    
    def load_model(self, path: str):
        """Load trained model."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.labels = data['labels']
            self.model_type = 'ml'

