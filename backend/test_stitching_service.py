from stitching_service import overlay_audio_on_video
from pathlib import Path

if __name__ == "__main__":
    AUDIO_DIR = Path("storage/audio")
    VIDEO_DIR = Path("storage/videos")
    AUDIO_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR = "storage/output"

    audio_file = f"{AUDIO_DIR}/test1.mp3"
    video_file = f"{VIDEO_DIR}/test1.mp4"
    output_file = f"{OUTPUT_DIR}/test1.mp4"
    overlay_audio_on_video(
        audio_file, video_file, output_file
    )  # print(f"Total duration: {sum(MOCK_DURATIONS)}s")
    # print(f"Number of dialog lines: {len(MOCK_DURATIONS)}")
    # print(f"First speaker: {FIRST_SPEAKER}")
    # print(f"\nGenerating video...")

    # output = overlay_speakers(
    #     video_path=VIDEO_PATH,
    #     rick_image_path=RICK_IMAGE,
    #     morty_image_path=MORTY_IMAGE,
    #     durations=MOCK_DURATIONS,
    #     first_speaker=FIRST_SPEAKER,
    #     output_path=OUTPUT_PATH,
    #     image_position=("center", "bottom"),  # Bottom center
    #     image_scale=0.25,
    # )

    # print(f"\nDone! Output saved to: {output}")
