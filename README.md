# MR-Team: Brainrot Video Generator 🧠📺

Transform boring lecture notes into engaging 30-second "brainrot" videos featuring Rick and Morty discussing your study material!

## Features

- 📄 **PDF Upload**: Upload lecture notes in PDF format
- 🤖 **AI Script Generation**: Converts your notes into a Rick & Morty dialogue
- 🎤 **Voice Synthesis**: Generates authentic Rick & Morty character voices
- 🎬 **Video Composition**: Combines dialogue with Minecraft parkour backgrounds
- 📱 **Vertical Format**: Optimized for TikTok, Reels, and Shorts (9:16 aspect ratio)

## Quick Start

### Prerequisites

- Python 3.11+
- FFmpeg (for audio/video processing)

### Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/generate` | Upload PDF to generate video |
| `GET` | `/status/{job_id}` | Check job status |
| `GET` | `/video/{job_id}` | Stream/display generated video |

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── main.py           # FastAPI server
├── requirements.txt  # Python dependencies
├── uploads/          # Uploaded PDF files
└── outputs/          # Generated videos
```

## Example Usage with cURL

```bash
# Generate a video from lecture notes
curl -X POST "http://localhost:8000/generate" \
  -F "pdf=@/path/to/lecture.pdf"

# Check status
curl "http://localhost:8000/status/{job_id}"

# Video URL (embed in frontend or open in browser)
# http://localhost:8000/video/{job_id}
```

## Tech Stack

- **FastAPI** - Python web framework
- **MoviePy** - Video editing
- **PyMuPDF** - PDF parsing

## License

MIT
