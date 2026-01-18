"""
Generate videos from PDF parser metadata.
Reads the audio_metadata.json created by the pdf_parser pipeline.

Run from backend folder: python generate_videos.py
"""

import json
from pathlib import Path
from image_service import process_segments

# Paths, all hardcoded. TODO: write in .env
SCRIPT_DIR = Path(__file__).parent
METADATA_FILE = SCRIPT_DIR / "data" / "audio_metadata.json"
VIDEO_PATH = SCRIPT_DIR / "video" / "brainrot" / "minecraft_parkour_video.mov"
RICK_IMAGE = SCRIPT_DIR / "images" / "rick.png"
MORTY_IMAGE = (
    SCRIPT_DIR / "images" / "rick-and-morty-rick-morty-projectacademy-medium-17.png"
)
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs" / "videos"


def load_metadata() -> dict:
    """Load the metadata JSON from the pdf_parser pipeline."""
    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_FILE}\n"
            "Run the pdf_parser pipeline first (dialogue_to_voice.py -> make_metadata.py)"
        )

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_videos() -> dict[str, str]:
    print("=" * 60)
    print("GENERATING VIDEOS FROM PDF PARSER METADATA")
    print("=" * 60)

    # Load metadata
    print(f"\nLoading metadata from: {METADATA_FILE}")
    metadata = load_metadata()

    print(f"Found {len(metadata)} segments\n")

    # Show what we're processing
    for segment_name, segment_data in metadata.items():
        num_lines = len(segment_data.get("transcripts", []))
        speakers = segment_data.get("person", [])
        print(f"  {segment_name}: {num_lines} lines, speakers: {speakers[:3]}...")

    print(f"\nVideo path: {VIDEO_PATH}")
    print(f"Rick image: {RICK_IMAGE}")
    print(f"Morty image: {MORTY_IMAGE}")
    print(f"Output dir: {OUTPUT_DIR}\n")

    # Generate videos
    output_paths = process_segments(
        segments_json=metadata,
        video_path=str(VIDEO_PATH),
        rick_image_path=str(RICK_IMAGE),
        morty_image_path=str(MORTY_IMAGE),
        output_dir=str(OUTPUT_DIR),
    )

    print(f"\n{'='*60}")
    print(f"✓ Done! Created {len(output_paths)} videos:")
    for segment_name, path in output_paths.items():
        print(f"  {segment_name} -> {path}")
    print("=" * 60)

    return output_paths
