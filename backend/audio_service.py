from pathlib import Path
import time
from typing import List

from moviepy import AudioFileClip, concatenate_audioclips


def merge_audio(audio_file_paths: List[Path], output_file: Path) -> Path:
    """Concatenate multiple audio files into `output_file` and return its Path."""
    if not audio_file_paths:
        raise ValueError("audio_file_paths must contain at least one Path")

    clips = []  # store all audio clips
    try:
        for p in audio_file_paths:
            if not p.exists() or not p.is_file():
                raise FileNotFoundError(f"Audio file not found: {p}")
            clips.append(AudioFileClip(str(p)))

        final_clip = clips[0] if len(clips) == 1 else concatenate_audioclips(clips)

        # Create output directory just in case
        out_dir = output_file.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        final_clip.write_audiofile(str(output_file), fps=44100)

        return output_file
    finally:
        for c in clips:
            try:
                c.close()
            except Exception:
                pass


# if __name__ == "__main__":
#     paths = [Path("storage/audio/test1.mp3"), Path("storage/audio/test2.mp3")]
#     output_path = Path("storage/audio/output.mp3")
#     output_path = merge_audio(paths, output_path)
#     print("Merged audio written to", output_path)
