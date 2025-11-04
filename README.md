# 🎯 FaceSharp (working title)

A service that evaluates technical sharpness and visual axes of faces (light, pose, jawline), and outputs a meme class: "god / mogged / sigma / average / meh / trash". Perfect for selfie quality checks before upload, filtering bad frames, and fun analytics.

**[🇷🇺 Read in Russian](README.ru.md)**

---

## What it does

- **Measures quality**: sharpness (Laplacian/Tenengrad/FFT), local contrast, exposure, noise, background bokeh
- **Understands face**: landmarks → proportions (cheekbones/jaw/eyes), jaw angle, yaw/pitch/roll, occlusions (glasses/mask/hand)
- **Provides axes (0–100)**: sharpness, lighting, pose, jawline, contrast
- **Meme label**: rule-based or ML classifier based on axes + embedding (CLIP/ArcFace): god / mogged / sigma / average / meh / trash
- **Explains results**: top factors lowering/raising score, and mini sharpness heatmap
- **Works on-device or via API**: privacy and low latency

## Architecture

### Backend (Python/FastAPI) ✅
- **Face Detection**: MediaPipe Face Detection + Face Mesh
- **Quality Metrics**: Laplacian, Tenengrad, FFT, RMS Contrast, Exposure
- **Geometry Analysis**: Pose estimation, jawline angle, proportions
- **Meme Classifier**: Rule-based (can be replaced with ML)

### Frontend (React) ✅
- Image upload
- Axes visualization (Radar chart)
- Results and reasons display
- Tags and quality score

### iOS App (SwiftUI) 📱
- Photo selection from gallery or camera
- API integration
- Beautiful UI with results

## Installation

### Requirements

- Python 3.12 (recommended) or Python 3.10+
- pip 24.0+
- Node.js 18+ (for frontend)

### Backend

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run API
cd api
python main.py
```

**Note**: Project is optimized for Python 3.12. See `PYTHON312_NOTES.md` for compatibility details.

API will be available at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**Important**: Run the dev server from the `frontend/` folder, not from the project root!

Frontend will be available at `http://localhost:3000`

### iOS App

1. Open `ios/FaceSharp.xcodeproj` in Xcode
2. Set the correct API URL in `FaceAnalysisViewModel.swift` (change `apiURL`)
3. For simulator testing, use your computer's local IP instead of `localhost`
4. Build and run the project

## API Endpoints

### POST `/analyze`
Analyzes a single image.

**Request**: multipart/form-data with `file` field

**Response**:
```json
{
  "ok": true,
  "axes": {
    "sharpness": 78,
    "lighting": 63,
    "pose": 84,
    "jawline": 72,
    "contrast": 69
  },
  "label": "sigma",
  "confidence": 0.81,
  "reasons": [
    "very high sharpness",
    "good lighting",
    "good angle/pose"
  ],
  "tags": ["blurry", "dark"],
  "quality": 75.5,
  "abstain": false,
  "model_version": "1.0.0"
}
```

### POST `/analyze/batch`
Analyzes multiple images in batch.

## How it works (pipeline)

1. **Face detection + alignment** (RetinaFace/Mediapipe, 5-point → similarity transform)
2. **Quality**: Laplacian/Tenengrad, FFT high-freq ratio, RMS contrast, exposure, local sharpness maps
3. **Geometry**: 468-points (FaceMesh) → distances/ratios, jaw angle, pose, occlusions
4. **Embedding** (optional): CLIP or ArcFace
5. **Scoring**: axes 0–100 + confidence calibration; rule or ML classifier outputs god/mogged/sigma/average/meh/trash
6. **Explain**: reasons and tips (e.g., "add light from left", "look at camera")

## Project Structure

```
FaceSharp/
├── api/                 # FastAPI backend
│   └── main.py
├── src/                 # Core analysis modules
│   ├── face_detection.py
│   ├── quality_metrics.py
│   ├── geometry_analysis.py
│   ├── meme_classifier.py
│   └── face_analyzer.py
├── frontend/            # React frontend
│   ├── src/
│   └── package.json
├── ios/                 # iOS SwiftUI app
│   └── FaceSharp/
└── requirements.txt
```

## Technologies

- **CV/ML**: OpenCV, Mediapipe (Face Detection/Mesh), PyTorch, open-clip
- **Classifier**: Logistic Regression / Linear SVM on concat(embedding, sharpness, geometry), probability calibration
- **API**: FastAPI/ONNX Runtime; optionally WebAssembly/TF.js for on-device mode
- **Frontend**: React (axis progress bars, heatmap, tips)
- **iOS**: SwiftUI

## Privacy & Ethics

- Does not evaluate "beauty" or appearance — only technical quality and meme categories for entertainment
- Photos are not saved by default; on-device mode available
- Built-in abstain for low confidence/poor conditions (light, extreme pose, occlusions)
- Validation on diverse shooting conditions; fairness metrics report

## Development Roadmap

- [ ] Sharpness heatmap by face zones, tips for improving frame
- [ ] Active learning in UI (labeling controversial cases)
- [ ] Batch folder processing and integrations (TG/Discord bot, Chrome extension)
- [ ] Threshold tuning for specific cameras/social networks
- [ ] ML classifier with embeddings (CLIP/ArcFace)

## License

MIT

## One-sentence teaser

"FaceSharp evaluates sharpness and key portrait axes, explains how to improve the frame, and — for fun — assigns a meme label 'god / mogged / sigma / average / meh / trash'."
