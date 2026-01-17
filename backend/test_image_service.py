"""
Test script for image_service
Run from backend folder: python test_image_service.py
"""
from image_service import overlay_speakers
import os

# Paths
VIDEO_PATH = "../video/brainrot/minecraft_parkour_video.mov"
RICK_IMAGE = "../images/rick.png"
MORTY_IMAGE = "../images/rick-and-morty-rick-morty-projectacademy-medium-17.png"
OUTPUT_PATH = "../outputs/test_output.mp4"

# Mock dialog durations (in seconds)
# Simulating a 30-second conversation
MOCK_DURATIONS = [
    3.0,   # Rick: "Morty, listen to me..."
    2.0,   # Morty: "Oh geez Rick..."
    4.0,   # Rick: "The mitochondria is the powerhouse..."
    2.5,   # Morty: "Wait, what?"
    3.5,   # Rick: "It's basic science Morty..."
    2.0,   # Morty: "I don't understand..."
    4.0,   # Rick: "That's because you're not paying attention..."
    2.5,   # Morty: "Okay okay I get it..."
    3.0,   # Rick: "Good. Now let's move on..."
    2.5,   # Morty: "Sure thing Rick..."
]

FIRST_SPEAKER = "rick"

# Create outputs folder if it doesn't exist
os.makedirs("../outputs", exist_ok=True)

if __name__ == "__main__":
    print(f"Total duration: {sum(MOCK_DURATIONS)}s")
    print(f"Number of dialog lines: {len(MOCK_DURATIONS)}")
    print(f"First speaker: {FIRST_SPEAKER}")
    print(f"\nGenerating video...")
    
    output = overlay_speakers(
        video_path=VIDEO_PATH,
        rick_image_path=RICK_IMAGE,
        morty_image_path=MORTY_IMAGE,
        durations=MOCK_DURATIONS,
        first_speaker=FIRST_SPEAKER,
        output_path=OUTPUT_PATH,
        image_position=("center", "bottom"),  # Bottom center
        image_scale=0.25,
    )
    
    print(f"\nDone! Output saved to: {output}")

