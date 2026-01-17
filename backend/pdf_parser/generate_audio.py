#!/usr/bin/env python3
"""
Main entry point for the PDF to Audio pipeline.

This script orchestrates the complete workflow:
1. Processes PDFs and generates cartoon dialogues
2. Converts dialogues to audio files (MP3)
3. Creates metadata JSON with timestamps and transcripts
"""

from dialogue_to_voice import dialogue_to_voice
from make_metadata import get_transcript_metadata


def main():
    """
    Main function to run the complete PDF to Audio pipeline.
    """
    print("="*80)
    print("PDF TO AUDIO PIPELINE")
    print("="*80)
    print("\nThis will:")
    print("  1. Extract text from PDFs")
    print("  2. Segment content using Claude API")
    print("  3. Convert to Rick & Morty dialogue")
    print("  4. Generate audio files (MP3)")
    print("  5. Create metadata with timestamps and transcripts")
    print("\n" + "="*80 + "\n")
    
    # Step 1: Generate dialogues and audio files
    print("\n" + "="*80)
    print("STEP 1: GENERATING AUDIO FILES")
    print("="*80 + "\n")
    
    results = dialogue_to_voice()
    
    if not results:
        print("\n✗ Failed to generate audio files. Exiting.")
        return False
    
    print(f"\n✓ Successfully generated {len(results)} audio segments")
    
    # Step 2: Create metadata with timestamps
    print("\n\n" + "="*80)
    print("STEP 2: CREATING METADATA")
    print("="*80 + "\n")
    
    metadata = get_transcript_metadata()
    
    if not metadata:
        print("\n✗ Failed to create metadata. Exiting.")
        return False
    
    print("\n✓ Successfully created metadata")
    
    # Final summary
    print("\n\n" + "="*80)
    print("PIPELINE COMPLETE")
    print("="*80 + "\n")
    
    total_segments = sum(len(metadata[key]["filename"]) for key in metadata if key.startswith("segment"))
    
    print(f"✓ Generated {total_segments} audio files")
    print(f"✓ Created metadata with transcripts and timestamps")
    print(f"✓ Output directory: backend/data/voice_output/")
    print(f"✓ Metadata file: backend/data/audio_metadata.json")
    
    print("\n" + "="*80)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
