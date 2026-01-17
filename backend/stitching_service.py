# import moviepy.editor as mpe
# from moviepy import *
from moviepy import *


# Assumes the video and audio file already exist.
# Given an audio file and a video file, overlays the audio fileo onto the video file, and save into the output file.
def overlay_audio_on_video(video_file, audio_file, output_file) -> str:
    try:
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)

        # Concatenate the video clip with the audio clip
        final_clip = video_clip.with_audio(audio_clip)
        final_clip.write_videofile(output_file)

    except Exception as e:
        print(f"Failed to overlay audio on video: {e}")
