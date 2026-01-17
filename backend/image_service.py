from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


def overlay_speakers(
    video_path: str,
    rick_image_path: str,
    morty_image_path: str,
    durations: list[float],
    first_speaker: str,  # "rick" or "morty"
    output_path: str,
    image_position: str | tuple = "center",  # "center" or (x, y)
    image_scale: float = 0.3,
) -> str:
    """
    Overlay Rick and Morty images on video based on dialog durations.
    Speakers alternate starting with first_speaker.
    
    Args:
        video_path: Path to the background video
        rick_image_path: Path to Rick's image (PNG with transparency recommended)
        morty_image_path: Path to Morty's image
        durations: List of durations in seconds for each dialog line
        first_speaker: "rick" or "morty" - who speaks first
        output_path: Path for the output video
        image_position: (x, y) position for the speaker image
        image_scale: Scale of image relative to video width
    
    Returns:
        Path to the output video
    """
    # Load the background video
    video = VideoFileClip(video_path)
    
    # Load speaker images with transparency
    rick_img = ImageClip(rick_image_path, transparent=True)
    morty_img = ImageClip(morty_image_path, transparent=True)
    
    # Scale images relative to video width
    target_width = int(video.w * image_scale)
    rick_img = rick_img.resized(width=target_width)
    morty_img = morty_img.resized(width=target_width)
    
    # Determine speaker order
    if first_speaker.lower() == "rick":
        speakers = [rick_img, morty_img]
    else:
        speakers = [morty_img, rick_img]
    
    # Create image clips for each dialog segment
    overlay_clips = []
    current_time = 0.0
    
    for i, duration in enumerate(durations):
        # Alternate between speakers
        img = speakers[i % 2]
        
        clip = (
            img
            .with_start(current_time)
            .with_duration(duration)
            .with_position(image_position)
        )
        overlay_clips.append(clip)
        current_time += duration
    
    # Composite all clips together
    final = CompositeVideoClip([video] + overlay_clips)
    
    # Write output
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )
    
    # Cleanup
    video.close()
    final.close()
    
    return output_path
