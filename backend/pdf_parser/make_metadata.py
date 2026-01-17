import os
import json
from pathlib import Path
from mutagen.mp3 import MP3


def get_mp3_duration(file_path):
    """
    Get the duration of an MP3 file in seconds.
    
    Args:
        file_path: Path to the MP3 file
        
    Returns:
        Duration in seconds as a float
    """
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0.0


def parse_filename(filename):
    """
    Parse the MP3 filename to extract segment number and person.
    
    Filename format: D{dialogue}_S{segment}_{speaker}.mp3
    Example: D1_S1_rick.mp3 -> segment 1, person: rick
    
    Args:
        filename: Name of the MP3 file
        
    Returns:
        Tuple of (segment_number, person)
    """
    # Remove .mp3 extension
    name = filename.replace('.mp3', '')
    
    # Extract segment number from D1, D2, D3, etc. (second character)
    if len(name) > 1 and name.startswith('D'):
        segment_char = name[1]  # Second character (1, 2, 3, etc.)
        try:
            segment_number = int(segment_char)
        except ValueError:
            segment_number = 0
    else:
        segment_number = 0
    
    # Extract person from last part after underscore
    parts = name.split('_')
    person = parts[-1] if parts else "unknown"
    
    return segment_number, person


def generate_timestamps(start_time, duration, interval=0.5):
    """
    Generate timestamps at regular intervals starting from a specific time.
    
    Args:
        start_time: Starting timestamp in seconds
        duration: Total duration in seconds
        interval: Time interval in seconds (default 0.5)
        
    Returns:
        List of timestamps
    """
    timestamps = []
    current = start_time
    end_time = start_time + duration
    
    while current <= end_time:
        timestamps.append(round(current, 1))
        current += interval
    
    return timestamps


def process_audio_files(audio_dir, metadata_skeleton):
    """
    Process all MP3 files and add timestamps and filename fields to existing metadata.
    
    Args:
        audio_dir: Path to directory containing MP3 files
        metadata_skeleton: Existing metadata with transcripts and person already filled
        
    Returns:
        Updated metadata dictionary with timestamps and filename added
    """
    audio_path = Path(audio_dir)
    
    if not audio_path.exists():
        print(f"Error: Directory '{audio_dir}' does not exist.")
        return metadata_skeleton
    
    # Get all MP3 files sorted by name
    mp3_files = sorted(list(audio_path.glob("*.mp3")))
    
    if not mp3_files:
        print(f"No MP3 files found in {audio_dir}")
        return metadata_skeleton
    
    print(f"\nProcessing {len(mp3_files)} MP3 files...")
    print(f"{'='*60}\n")
    
    # Process each file
    for mp3_file in mp3_files:
        filename = mp3_file.name
        
        # Get duration
        duration = get_mp3_duration(str(mp3_file))
        
        # Parse filename
        segment_number, person = parse_filename(filename)
        
        # Get segment key
        segment_key = f"segment {segment_number}"
        
        if segment_key in metadata_skeleton:
            # Just add the duration to timestamps list
            metadata_skeleton[segment_key]["timestamps"].append(duration)
            metadata_skeleton[segment_key]["filename"].append(filename)
            
            print(f"✓ {filename}")
            print(f"  Segment: {segment_number}, Person: {person}, Duration: {duration:.2f}s\n")
    
    print(f"{'='*60}")
    print("Processing complete!\n")
    
    # Convert durations to cumulative timestamps with 0.5s intervals
    print("Converting to cumulative timestamps...\n")
    for segment_key in ["segment 1", "segment 2", "segment 3"]:
        durations = metadata_skeleton[segment_key]["timestamps"]
        if durations:
            cumulative_timestamps = []
            cumulative_time = 0.0
            
            for i, duration in enumerate(durations):
                if i == 0:
                    # First file: just use the duration
                    cumulative_time = duration
                else:
                    # Subsequent files: add 0.5s interval + duration
                    cumulative_time = cumulative_time + 0.5 + duration
                
                cumulative_timestamps.append(cumulative_time)
            
            # Replace durations with cumulative timestamps
            metadata_skeleton[segment_key]["timestamps"] = cumulative_timestamps
            
            print(f"{segment_key.title()}: {durations[:3]} → {cumulative_timestamps[:3]}")
    
    print()
    
    # Print summary
    for segment_key in ["segment 1", "segment 2", "segment 3"]:
        count = len(metadata_skeleton[segment_key]["filename"])
        print(f"{segment_key.title()}: {count} files")
    
    return metadata_skeleton


def save_to_json(data, output_path):
    """
    Save the metadata dictionary to a JSON file.
    
    Args:
        data: Dictionary to save
        output_path: Path to output JSON file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved metadata to: {output_file}")


def main():
    """Main function to process audio files and add remaining metadata fields."""
    # Get the directory paths
    script_dir = Path(__file__).parent
    audio_dir = script_dir.parent / "data" / "voice_output"
    metadata_file = script_dir.parent / "data" / "audio_metadata.json"
    
    print(f"Audio directory: {audio_dir}")
    print(f"Metadata file: {metadata_file}")
    
    # Load existing metadata skeleton (created by chunk_to_cartoon.py)
    if metadata_file.exists():
        print("\n✓ Loading existing metadata skeleton...")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"  Found transcripts and person fields already populated")
    else:
        print("\n⚠ Warning: Metadata skeleton not found!")
        print("  Run chunk_to_cartoon.py first or dialogue_to_voice.py to create skeleton")
        return None
    
    # Add timestamps and filename fields
    metadata = process_audio_files(audio_dir, metadata)
    
    # Save updated metadata
    if metadata:
        save_to_json(metadata, metadata_file)
        
        # Print sample of the data structure
        print("\n" + "="*60)
        print("FINAL METADATA STRUCTURE")
        print("="*60)
        
        for segment_key in ["segment 1", "segment 2", "segment 3"]:
            if metadata[segment_key]["filename"]:
                print(f"\n{segment_key.upper()}:")
                print(f"  Files: {len(metadata[segment_key]['filename'])}")
                print(f"  Transcripts: {len(metadata[segment_key]['transcripts'])}")
                print(f"  People: {metadata[segment_key]['person'][:2]}...")
                if metadata[segment_key]["timestamps"]:
                    print(f"  Timestamps: {metadata[segment_key]['timestamps'][:2]}...")
                if metadata[segment_key]["transcripts"]:
                    print(f"  Sample transcript: {metadata[segment_key]['transcripts'][0][:60]}...")
    
    return metadata


if __name__ == "__main__":
    main()
