import os
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="MR-Team: Brainrot Video Generator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories on startup
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class GenerateResponse(BaseModel):
    job_id: str
    message: str


@app.get("/")
def health_check():
    return {"status": "ok", "service": "mr-team"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_video(pdf: UploadFile = File(...)):
    """Upload PDF and generate brainrot video."""
    
    if not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")
    
    job_id = str(uuid.uuid4())
    
    # Save uploaded PDF
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(await pdf.read())
    
    # TODO: Process the PDF and generate video
    # 1. Extract text from PDF
    # 2. Generate Rick & Morty script with OpenAI
    # 3. Generate audio
    # 4. Compose video with brainrot background
    
    return GenerateResponse(
        job_id=job_id,
        message="PDF uploaded successfully"
    )


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Check job status."""
    pdf_exists = (UPLOAD_DIR / f"{job_id}.pdf").exists()
    video_exists = (OUTPUT_DIR / f"{job_id}.mp4").exists()
    
    if not pdf_exists:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job_id,
        "status": "completed" if video_exists else "processing",
    }


@app.get("/video/{job_id}")
def get_video(job_id: str):
    """Stream video for display."""
    video_path = OUTPUT_DIR / f"{job_id}.mp4"
    
    if not video_path.exists():
        raise HTTPException(404, "Video not found")
    
    return FileResponse(video_path, media_type="video/mp4")
