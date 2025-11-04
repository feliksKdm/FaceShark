"""FastAPI backend for FaceSharp."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
import io
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.face_analyzer import FaceAnalyzer

app = FastAPI(title="FaceSharp API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = FaceAnalyzer(model_version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "FaceSharp",
        "version": "1.0.0",
        "description": "Face quality assessment with meme labels"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze face in uploaded image.
    
    Returns:
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
        "reasons": [...],
        "abstain": false,
        "model_version": "1.0.0"
    }
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Analyze
        result = analyzer.analyze_image(image)
        
        # Convert to dict for JSON response
        result_dict = {
            "ok": result.ok,
            "axes": result.axes,
            "label": result.label,
            "confidence": result.confidence,
            "reasons": result.reasons,
            "abstain": result.abstain,
            "model_version": result.model_version
        }
        
        # Optionally include pose and proportions
        if result.pose:
            result_dict["pose"] = result.pose
        if result.proportions:
            result_dict["proportions"] = result.proportions
        
        return JSONResponse(content=result_dict)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/batch")
async def analyze_batch(files: list[UploadFile] = File(...)):
    """Analyze multiple images in batch."""
    results = []
    
    for file in files:
        try:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                results.append({
                    "filename": file.filename,
                    "ok": False,
                    "error": "Invalid image format"
                })
                continue
            
            result = analyzer.analyze_image(image)
            results.append({
                "filename": file.filename,
                "ok": result.ok,
                "axes": result.axes,
                "label": result.label,
                "confidence": result.confidence
            })
        
        except Exception as e:
            results.append({
                "filename": file.filename,
                "ok": False,
                "error": str(e)
            })
    
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

