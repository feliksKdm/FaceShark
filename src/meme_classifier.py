"""Extended meme classifier with tags & quality."""
from typing import Dict, List, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle

class MemeClassifier:
    """
    Works on 5 axes (0..100): sharpness, lighting, pose, jawline, contrast.
    Returns: (label, confidence, reasons, tags, quality)
    """
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.labels = ['god', 'mogged', 'sigma', 'average', 'meh', 'trash']
        self.model_type = 'rule_based'

        self.weights = {
            'sharpness': 0.30, 'lighting': 0.18, 'pose': 0.20, 'jawline': 0.22, 'contrast': 0.10,
        }
        self.TH = {
            'blurry': 45, 'very_blurry': 30, 'dark': 42, 'overexposed': 88,
            'bad_pose': 55, 'weak_jaw': 52, 'low_contrast': 45,
        }
        self.TIERS = {
            'god':     {'min': 87, 'keys': {'sharpness': 80, 'jawline': 75, 'pose': 75}},
            'mogged':  {'min': 78, 'keys': {'sharpness': 72, 'jawline': 70, 'pose': 68}},
            'sigma':   {'min': 65, 'keys': {'sharpness': 60, 'jawline': 58}, 'min_axis': 50},
            'average': {'min': 55},
        }

    # -------- helpers --------
    def _composite(self, axes: Dict[str, float]) -> float:
        score = 0.0
        for k, w in self.weights.items():
            v = max(0.0, min(100.0, float(axes.get(k, 50.0))))
            score += w * v
        penalties = 0.0
        bad_axes = []
        for k in ['sharpness','lighting','pose','jawline','contrast']:
            v = float(axes.get(k, 50.0))
            if v < 45:
                bad_axes.append(k)
                # lighting/contrast get lighter penalties than sharpness/pose/jawline
                factor = 0.06 if k in ('lighting', 'contrast') else 0.09
                penalties += (45 - v) * factor
            if v < 30:
                factor = 0.12 if k in ('lighting', 'contrast') else 0.18
                penalties += (30 - v) * factor
            if bad_axes:
                penalties = min(penalties, 8.0 + 3.0 * max(0, len(bad_axes)-1))
        return max(0.0, min(100.0, score - penalties))

    def _tags(self, axes: Dict[str, float]) -> List[str]:
        s = float(axes.get('sharpness', 50)); l = float(axes.get('lighting', 50))
        p = float(axes.get('pose', 50)); j = float(axes.get('jawline', 50)); c = float(axes.get('contrast', 50))
        th = self.TH
        tags = []
        if s < th['very_blurry']: tags.append('very_blurry')
        elif s < th['blurry']:    tags.append('blurry')
        if l < th['dark']:        tags.append('dark')
        if l > th['overexposed']: tags.append('overexposed')
        if p < th['bad_pose']:    tags.append('bad_pose')
        if j < th['weak_jaw']:    tags.append('weak_jaw')
        if c < th['low_contrast']:tags.append('low_contrast')
        return tags

    def _reasons(self, axes: Dict[str, float]) -> List[str]:
        pos, neg = [], []
        s = axes.get('sharpness', 50); l = axes.get('lighting', 50)
        p = axes.get('pose', 50); j = axes.get('jawline', 50); c = axes.get('contrast', 50)
        if s >= 80: pos.append("very high sharpness")
        if l >= 72: pos.append("good lighting")
        if p >= 80: pos.append("good angle/pose")
        if j >= 76: pos.append("strong jawline")
        if c >= 70: pos.append("sufficient contrast")
        if s < 45: neg.append("low sharpness")
        if l < 45: neg.append("insufficient lighting")
        if p < 55: neg.append("suboptimal pose/angle")
        if j < 52: neg.append("weak jawline")
        if c < 45: neg.append("low contrast")
        return pos + neg

    

    # -------- decision --------
    def classify_rule_based(self, axes: Dict[str, float]) -> Tuple[str, float, List[str], List[str], float]:
        axes = {k: float(axes.get(k, 50.0)) for k in ['sharpness','lighting','pose','jawline','contrast']}
        tags = self._tags(axes)
        reasons = self._reasons(axes)
        quality = self._composite(axes)
        min_axis = min(axes.values())
        very_bad_axes = sum(v < 30 for v in axes.values())



        # --- HERO-FACE OVERRIDE ---
        core_ok = (
            axes['sharpness'] >= 78 and
            axes['jawline']   >= 54 and
            axes['pose']      >= 60
        )
        if core_ok:
            # If quality already high → mogged, else sigma
            if quality >= 75 or (axes['sharpness'] >= 75 and axes['jawline'] >= 72):
                conf = 0.80 + min(0.20, (quality - 80) / 20.0)
                return 'mogged', float(min(conf, 0.96)), reasons, tags, float(quality)
            else:
                conf = 0.70 + min(0.20, max(0.0, quality - 70) / 20.0)
                return 'sigma', float(min(conf, 0.90)), reasons, tags, float(quality)
        if very_bad_axes >= 2 or (quality < 45 and ('very_blurry' in tags or 'dark' in tags)):
            conf = 0.68 + max(0, (55 - quality)) / 55 * 0.25
            return 'trash', float(min(conf, 0.96)), reasons, tags, float(quality)

        if quality < 50:
            return 'meh', 0.60, reasons, tags, float(quality)
        if quality < 62 or min_axis < 48:
            return 'average', 0.55, reasons, tags, float(quality)

        for tier in ['god', 'mogged', 'sigma']:
            rule = self.TIERS[tier]
            if quality >= rule['min']:
                keys_ok = all(axes.get(k, 0) >= v for k, v in rule.get('keys', {}).items())
                min_axis_ok = (min_axis >= rule.get('min_axis', 0))
                if keys_ok and min_axis_ok:
                    margin = max(0, quality - rule['min'])
                    base, cap = {'god': (0.75, 0.22), 'mogged': (0.67, 0.25), 'sigma': (0.60, 0.27)}[tier]
                    conf = base + min(cap, margin / 15.0)
                    return tier, float(min(conf, 0.98)), reasons, tags, float(quality)

        label = 'average' if quality >= 62 and min_axis >= 55 else 'meh'
        conf = 0.54 if label == 'average' else 0.56
        return label, float(conf), reasons, tags, float(quality)

    def classify(self, axes: Dict[str, float], embedding: np.ndarray = None):
        if self.model_type == 'rule_based':
            return self.classify_rule_based(axes)
        return self.classify_ml(axes, embedding)

    # --- ML placeholders ---
    def classify_ml(self, axes: Dict[str, float], embedding: np.ndarray):
        return self.classify_rule_based(axes)

    def train(self, features: np.ndarray, labels: np.ndarray):
        feats = self.scaler.fit_transform(features)
        self.model = LogisticRegression(multi_class='multinomial', max_iter=1000)
        self.model.fit(feats, labels)
        self.model_type = 'ml'

    def save_model(self, path: str):
        if self.model:
            with open(path, 'wb') as f:
                pickle.dump({'model': self.model, 'scaler': self.scaler, 'labels': self.labels}, f)

    def load_model(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']; self.scaler = data['scaler']; self.labels = data['labels']
            self.model_type = 'ml'
