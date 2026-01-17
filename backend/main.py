import os
import uuid
from pathlib import Path
from stitching_service import overlay_audio_on_video
from job_service import job_service
from video_metadata_service import video_metadata_service

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
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
    # 3. Generate audio -> return audio files
    # 4. Compose video with brainrot background

    # Darren returns { chunkId: audiometadata[], }
    # For each chunk:
    # Kai stitches images onto background video for one chunk -> returns video paths
    # image_service.stitch(chunkToAudio) -> { chunkId: videoPaths[] }
    # audio_service.merge(audioPaths[]) -> audioPath
    # stitching_service.overlay_audio_and_video(videoPath, audioPath) -> output_video_path

    # Merge audio files tgt into one audio file
    # Merge audio files for one video into one audio file
    # Merge background with

    return GenerateResponse(job_id=job_id, message="PDF uploaded successfully")


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Check job status."""

    status = job_service.get_status(job_id)
    if not status:
        raise HTTPException(404, "Job not found")

    return {"job_id": job_id, "status": status.name.lower()}


@app.get("/videos/{job_id}/list")
def get_videos_list(job_id: str):
    """Get list of video IDs for a given job."""

    status = job_service.get_status(job_id)
    if not status:
        raise HTTPException(404, "Job not found")

    video_ids = job_service.get_videos(job_id)
    # video_ids = [video.stem for video in videos]  # Extract filename without extension

    return {"job_id": job_id, "videos": video_ids, "count": len(video_ids)}


# Helper to stream video
def stream_video(video_path: Path, request: Request):
    CHUNK_SIZE = 1024 * 1024

    if not video_path.exists() or not video_path.is_file():
        raise HTTPException(404, "Video not found")

    range_header = request.headers.get("range")
    print("HI", range_header)
    if not range_header:
        return FileResponse(video_path, media_type="video/mp4")

    file_size = video_path.stat().st_size
    byte_range = range_header.replace("bytes=", "").split("-", 1)
    try:
        start = int(byte_range[0]) if byte_range[0] else 0
        end = int(byte_range[1]) if byte_range[1] else file_size - 1
    except ValueError as exc:
        raise HTTPException(416, "Invalid range") from exc

    if start >= file_size:
        raise HTTPException(416, "Range not satisfiable")

    end = min(end, file_size - 1)
    content_length = end - start + 1

    def iterfile() -> Iterator[bytes]:
        with open(video_path, "rb") as file_handle:
            file_handle.seek(start)
            remaining = content_length
            while remaining > 0:
                chunk = file_handle.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk  # returns a Generator

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
    }
    return StreamingResponse(
        iterfile(),
        status_code=206,
        media_type="video/mp4",
        headers=headers,
    )


@app.get("/videos/{video_id}")
def get_single_video(video_id: str, request: Request):
    """Stream a single video for display."""

    video_metadata = video_metadata_service.get_video_metadata(video_id)

    if not video_metadata:
        raise HTTPException(404, "Video not found")

    video_path = video_metadata.video_path

    if not video_path or not video_path.exists():
        raise HTTPException(404, "Video file not found on disk")

    return stream_video(video_path, request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
