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
    
    # Extract segment number from D1, D2, D3, etc.
    if name.startswith('D'):
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


def generate_timestamps(duration, interval=0.5):
    """
    Generate timestamps at regular intervals.
    
    Args:
        duration: Total duration in seconds
        interval: Time interval in seconds (default 0.5)
        
    Returns:
        List of timestamps
    """
    timestamps = []
    current = 0.0
    
    while current <= duration:
        timestamps.append(round(current, 1))
        current += interval
    
    return timestamps


def process_audio_files(audio_dir):
    """
    Process all MP3 files in the directory and organize by segment.
    
    Args:
        audio_dir: Path to directory containing MP3 files
        
    Returns:
        Dictionary organized by segments
    """
    audio_path = Path(audio_dir)
    
    if not audio_path.exists():
        print(f"Error: Directory '{audio_dir}' does not exist.")
        return {}
    
    # Initialize result dictionary
    result = {
        "segment 1": {
            "timestamps": [],
            "transcripts": [],
            "person": [],
            "filename": []
        },
        "segment 2": {
            "timestamps": [],
            "transcripts": [],
            "person": [],
            "filename": []
        },
        "segment 3": {
            "timestamps": [],
            "transcripts": [],
            "person": [],
            "filename": []
        }
    }
    
    # Get all MP3 files
    mp3_files = sorted(list(audio_path.glob("*.mp3")))
    
    if not mp3_files:
        print(f"No MP3 files found in {audio_dir}")
        return result
    
    print(f"\nProcessing {len(mp3_files)} MP3 files...")
    print(f"{'='*60}\n")
    
    # Process each file
    for mp3_file in mp3_files:
        filename = mp3_file.name
        
        # Get duration
        duration = get_mp3_duration(str(mp3_file))
        
        # Parse filename
        segment_number, person = parse_filename(filename)
        
        # Generate timestamps
        timestamps = generate_timestamps(duration)
        
        # Add to appropriate segment
        segment_key = f"segment {segment_number}"
        
        if segment_key in result:
            result[segment_key]["timestamps"].append(timestamps)
            result[segment_key]["transcripts"].append("")  # Empty for now
            result[segment_key]["person"].append(person)
            result[segment_key]["filename"].append(filename)
            
            print(f"✓ {filename}")
            print(f"  Segment: {segment_number}, Person: {person}, Duration: {duration:.2f}s")
            print(f"  Timestamps: {len(timestamps)} intervals (0.5s each)\n")
    
    print(f"{'='*60}")
    print("Processing complete!\n")
    
    # Print summary
    for segment_key in ["segment 1", "segment 2", "segment 3"]:
        count = len(result[segment_key]["filename"])
        print(f"{segment_key.title()}: {count} files")
    
    return result


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
    """Main function to process audio files and generate metadata."""
    # Get the directory paths
    script_dir = Path(__file__).parent
    audio_dir = script_dir.parent / "data" / "voice_output"
    output_file = script_dir.parent / "data" / "audio_metadata.json"
    
    print(f"Audio directory: {audio_dir}")
    print(f"Output file: {output_file}")
    
    # Process files
    metadata = process_audio_files(audio_dir)
    
    # Save to JSON
    if metadata:
        save_to_json(metadata, output_file)
        
        # Print sample of the data structure
        print("\n" + "="*60)
        print("SAMPLE OUTPUT STRUCTURE")
        print("="*60)
        
        for segment_key in ["segment 1", "segment 2", "segment 3"]:
            if metadata[segment_key]["filename"]:
                print(f"\n{segment_key.upper()}:")
                print(f"  Files: {metadata[segment_key]['filename'][:2]}...")
                print(f"  People: {metadata[segment_key]['person'][:2]}...")
                if metadata[segment_key]["timestamps"]:
                    print(f"  Sample timestamps: {metadata[segment_key]['timestamps'][0][:5]}...")
    
    return metadata


if __name__ == "__main__":
    main()
