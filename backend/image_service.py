from moviepy import VideoFileClip, ImageClip, CompositeVideoClip


def overlay_speakers(
    video_path: str,
    rick_image_path: str,
    morty_image_path: str,
    durations: list[float],
    speakers: list[str],  # ["rick", "morty", "rick", ...] in order
    output_path: str,
    image_position: str | tuple = ("center", "bottom"),
    image_scale: float = 0.3,
    start_time: float = 0.0,  # When the first speaker starts
    end_time: float = None,  # When to cut off the video (last_timestamp + buffer)
) -> str:
    """
    Overlay Rick and Morty images on video based on dialog durations.
    
    Args:
        video_path: Path to the background video
        rick_image_path: Path to Rick's image (PNG with transparency recommended)
        morty_image_path: Path to Morty's image
        durations: List of durations in seconds for each dialog line
        speakers: List of speakers in order ("rick" or "morty")
        output_path: Path for the output video
        image_position: Position for the speaker image
        image_scale: Scale of image relative to video width
        start_time: When the first speaker starts appearing (in seconds)
        end_time: When to cut off the video (if None, uses full video length)
    
    Returns:
        Path to the output video
    """
    # Load the background video
    video = VideoFileClip(video_path)
    
    # Trim video to end_time if specified
    if end_time is not None:
        video = video.subclipped(0, min(end_time, video.duration))
    
    # Load speaker images with transparency
    rick_img = ImageClip(rick_image_path, transparent=True)
    morty_img = ImageClip(morty_image_path, transparent=True)
    
    # Scale images relative to video width
    target_width = int(video.w * image_scale)
    rick_img = rick_img.resized(width=target_width)
    morty_img = morty_img.resized(width=target_width)
    
    # Create image clips for each dialog segment
    overlay_clips = []
    current_time = start_time  # Start from the first timestamp
    
    for i, (duration, speaker) in enumerate(zip(durations, speakers)):
        # Select the correct speaker image
        img = rick_img if speaker.lower() == "rick" else morty_img
        
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


def process_segments(
    segments_json: dict,
    video_path: str,
    rick_image_path: str,
    morty_image_path: str,
    output_dir: str,
) -> list[str]:
    """
    Process multiple segments from the PDF parser JSON and create videos.
    
    Args:
        segments_json: JSON with segment data (timestamps, person, etc.)
        video_path: Path to the brainrot background video
        rick_image_path: Path to Rick's image
        morty_image_path: Path to Morty's image
        output_dir: Directory to save output videos
    
    Returns:
        List of output video paths
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    output_paths = []
    
    for segment_name, segment_data in segments_json.items():
        print(f"Processing {segment_name}...")
        
        # Extract data from segment
        speakers = segment_data["person"]
        timestamps = segment_data["timestamps"]
        
        # Calculate durations from timestamps
        # First speaker starts at 0s, timestamps mark when each speaker ENDS
        # So: duration[0] = timestamps[0] - 0
        #     duration[i] = timestamps[i] - timestamps[i-1]
        durations = []
        for i in range(len(timestamps)):
            if i == 0:
                duration = timestamps[0]  # First speaker: 0 to timestamp[0]
            else:
                duration = timestamps[i] - timestamps[i - 1]
            durations.append(duration)
        
        # Calculate video end time (last timestamp + 10 seconds buffer)
        last_timestamp = timestamps[-1]
        video_end_time = last_timestamp + 10.0
        
        print(f"  Timestamps (end times): {timestamps}")
        print(f"  Durations: {durations}")
        print(f"  Video will end at: {video_end_time}s (last timestamp + 10s)")
        
        # Output path for this segment
        output_path = os.path.join(output_dir, f"{segment_name.replace(' ', '_')}.mp4")
        
        # Create the video
        result = overlay_speakers(
            video_path=video_path,
            rick_image_path=rick_image_path,
            morty_image_path=morty_image_path,
            durations=durations,
            speakers=speakers,
            output_path=output_path,
            start_time=0.0,  # First speaker starts at 0s
            end_time=video_end_time,  # Cut video 10s after last timestamp
        )
        
        output_paths.append(result)
        print(f"  ✓ Created {output_path}")
    
    return output_paths
