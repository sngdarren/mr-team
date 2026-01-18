import os
import uuid
from pathlib import Path
from stitching_service import overlay_audio_on_video
from job_service import job_service
from audio_service import merge_audio
from video_metadata_service import video_metadata_service
from pdf_parser.pdf_plumber import extract_text_from_pdf
from pdf_parser.generate_audio import generate_audio
from generate_videos import generate_videos, load_metadata

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
UPLOAD_DIR = Path("data/pdf_data")
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

    try:
        # Save uploaded PDF
        pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(await pdf.read())

        job_service.create_job(job_id)

        # Load metadata to get audio filenames for each segment
        metadata = load_metadata()

        # Generate videos for each segment
        segment_to_vid_path = generate_videos()

        # For each segment, get audio files and process
        for segment_name, vid_path in segment_to_vid_path.items():
            segment_metadata = metadata[segment_name]
            audio_filenames = segment_metadata.get("filename", [])

            # Convert filenames to full paths (e.g., "D1_S1_rick.mp3" -> "data/voice_output/D1_S1_rick.mp3")
            AUDIO_DIR = Path("data/voice_output")
            MERGED_AUDIO_OUTPUT_DIR = Path("audio")
            audio_paths = [AUDIO_DIR / filename for filename in audio_filenames]

            # Merge audio files for this segment
            merged_audio_filename = f"{segment_name.replace(' ', '_')}_merged.mp3"
            merged_audio_path = merge_audio(
                audio_paths, MERGED_AUDIO_OUTPUT_DIR / merged_audio_filename
            )

            # Overlay audio onto video for this segment
            video_id = str(uuid.uuid4())
            final_video_path = OUTPUT_DIR / f"{video_id}.mp4"
            final_video_path = overlay_audio_on_video(
                str(vid_path), str(merged_audio_path), str(final_video_path)
            )

            # Add video to job and metadata service
            job_service.add_video(job_id, final_video_path)
            video_metadata_service.add_video_metadata(video_id, final_video_path)

        # Mark job as done
        job_service.mark_done(job_id)

    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        raise

        # extracted_text = extract_text_from_pdf(str(pdf_path))
        # if not extracted_text or not extracted_text.strip():
        #     raise HTTPException(400, "No extractable text found in PDF")

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
        # update JOB and VIDEOMETADATA

        # background_video_path = Path("storage/outputs/minecraft_parkour_video.mp4")
        # if not background_video_path.exists():
        #     raise HTTPException(500, "Background video missing")

        # video_id = str(uuid.uuid4())
        # output_video_path = OUTPUT_DIR / f"{video_id}.mp4"
        # if not output_video_path.exists():
        #     try:
        #         output_video_path.symlink_to(background_video_path)
        #     except OSError:
        #         os.link(background_video_path, output_video_path)

        # video_metadata_service.add_video_metadata(video_id, output_video_path)
        # job_service.set_videos(job_id, [video_id])
        # job_service.mark_done(job_id)

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
