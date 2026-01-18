import os
import asyncio
import re
import requests
from pathlib import Path
from dotenv import load_dotenv
from pdf_parser.chunk_to_cartoon import pdf_to_cartoon_chunk

# Load environment variables
load_dotenv()

# Output directory for voice files (absolute path to root-level data folder)
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "voice_output"
# CREATE IF DOESNT EXIT
OUTPUT_DIR.mkdir(exist_ok=True)

# Voice model IDs for each character
VOICE_MODELS = {
    "rick": "ada3fab76e534bba88c08a94a72413fb",
    "morty": "377e4ac186da47faa3b644d033775954",
}


def split_dialogue_by_speaker(dialogue_text):
    """
    Split a dialogue string by [rick] and [morty] delimiters.

    Args:
        dialogue_text: String containing dialogue with [rick] and [morty] markers

    Returns:
        List of tuples: [(speaker, text), (speaker, text), ...]
    """
    # Find all speaker tags and their positions
    pattern = r"\[(rick|morty)\]\s*"

    segments = []
    matches = list(re.finditer(pattern, dialogue_text, re.IGNORECASE))

    for i, match in enumerate(matches):
        speaker = match.group(1).lower()
        start = match.end()

        # Get the text until the next speaker or end of string
        if i < len(matches) - 1:
            end = matches[i + 1].start()
        else:
            end = len(dialogue_text)

        text = dialogue_text[start:end].strip()

        if text:  # Only add if there's actual content
            segments.append({"speaker": speaker, "text": text})

    return segments


async def call_tts_api(text, speaker, segment_id, semaphore=None):
    """
    Call Fish Audio TTS API to convert text to speech.

    Args:
        text: The text to convert to speech
        speaker: 'rick' or 'morty'
        segment_id: Identifier for this segment
        semaphore: Optional asyncio.Semaphore to limit concurrent requests

    Returns:
        Tuple of (audio_data, success) where audio_data is bytes or None
    """
    api_token = os.getenv("FISH_API_TOKEN")
    if not api_token:
        print(f"  ✗ Error: FISH_API_TOKEN not found for {segment_id}")
        return None, False

    # Get the model ID for the speaker
    model_id = VOICE_MODELS.get(speaker.lower())
    if not model_id:
        print(f"  ✗ Error: Unknown speaker '{speaker}' for {segment_id}")
        return None, False

    url = "https://api.fish.audio/v1/tts"

    payload = {
        "text": text,
        "reference_id": model_id,
        "temperature": 0.7,
        "top_p": 0.7,
        "chunk_length": 300,
        "normalize": True,
        "format": "mp3",
        "mp3_bitrate": 128,
        "latency": "normal",
        "max_new_tokens": 1024,
        "repetition_penalty": 1.2,
        "min_chunk_length": 50,
        "condition_on_previous_chunks": True,
        "early_stop_threshold": 1,
    }

    headers = {
        "model": "s1",
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    try:
        print(f"  → Calling TTS API for {segment_id} ({speaker})...")

        # Use semaphore to limit concurrent requests if provided
        async with semaphore if semaphore else asyncio.Semaphore(1):
            # Run the blocking requests call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: requests.post(url, json=payload, headers=headers)
            )

        response.raise_for_status()

        print(f"  ✓ TTS API completed for {segment_id}")
        return response.content, True

    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP Error for {segment_id}: {e}")
        print(f"     Response: {response.text if response else 'No response'}")
        return None, False
    except Exception as e:
        print(f"  ✗ Error calling TTS API for {segment_id}: {e}")
        return None, False


async def process_dialogue_segment(
    segment, dialogue_index, segment_index, output_dir=None, semaphore=None
):
    """
    Process a single dialogue segment and convert to audio.

    Args:
        segment: Dictionary with 'speaker' and 'text'
        dialogue_index: Index of the parent dialogue
        segment_index: Index of this segment within the dialogue
        output_dir: Optional directory to save audio files
        semaphore: Optional asyncio.Semaphore to limit concurrent API requests

    Returns:
        Dictionary with processed segment info including audio data
    """
    segment_id = f"D{dialogue_index}_S{segment_index}_{segment['speaker']}"

    print(f"  → Processing {segment_id}: {segment['text'][:50]}...")

    # Call TTS API
    audio_data, success = await call_tts_api(
        segment["text"], segment["speaker"], segment_id, semaphore
    )

    result = {
        "dialogue_index": dialogue_index,
        "segment_index": segment_index,
        "speaker": segment["speaker"],
        "text": segment["text"],
        "segment_id": segment_id,
        "audio_data": audio_data,
        "success": success,
    }

    # Optionally save audio to file
    if success and audio_data and output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        audio_file = output_path / f"{segment_id}.mp3"

        with open(audio_file, "wb") as f:
            f.write(audio_data)

        result["audio_file"] = str(audio_file)
        print(f"  ✓ Saved audio to {audio_file}")

    return result


async def process_all_dialogues():
    """
    Process all dialogues from pdf_to_cartoon_chunk and split them by speaker.
    Creates async tasks for each speaker segment.

    Returns:
        List of processed segments ready for API calls
    """
    print("Getting cartoon dialogues...\n")
    dialogues = await pdf_to_cartoon_chunk()

    if not dialogues:
        print("No dialogues to process")
        return []

    print(f"\n{'='*60}")
    print(f"Processing {len(dialogues)} dialogues")
    print(f"{'='*60}\n")

    # Create semaphore to limit concurrent API requests (max 3 at a time)
    semaphore = asyncio.Semaphore(3)

    # Collect all segments and create async tasks
    all_tasks = []

    for dialogue_index, dialogue in enumerate(dialogues, 1):
        print(f"\nDialogue {dialogue_index}:")
        print(f"{'='*60}")

        # Split dialogue by speaker
        segments = split_dialogue_by_speaker(dialogue)

        print(f"Found {len(segments)} speaker segments")

        # Create async task for each segment
        for segment_index, segment in enumerate(segments, 1):
            task = process_dialogue_segment(
                segment,
                dialogue_index,
                segment_index,
                output_dir=str(OUTPUT_DIR),
                semaphore=semaphore,
            )
            all_tasks.append(task)

    print(f"\n{'='*60}")
    print(f"Processing {len(all_tasks)} segments concurrently...")
    print(f"{'='*60}\n")

    # Run all segments concurrently
    results = await asyncio.gather(*all_tasks)

    print(f"\n{'='*60}")
    print(f"All segments processed! Total: {len(results)}")
    print(f"{'='*60}")

    return results


def dialogue_to_voice():
    """
    Main function to convert dialogues to voice-ready segments.

    Returns:
        List of processed segments ready for voice API
    """
    results = asyncio.run(process_all_dialogues())

    # Print summary
    print(f"\n\n{'='*60}")
    print("FINAL VOICE SEGMENTS SUMMARY")
    print(f"{'='*60}\n")

    rick_count = sum(1 for r in results if r["speaker"] == "rick")
    morty_count = sum(1 for r in results if r["speaker"] == "morty")

    print(f"Total segments: {len(results)}")
    print(f"Rick segments: {rick_count}")
    print(f"Morty segments: {morty_count}\n")

    # Show first few segments as examples
    print("Sample segments:")
    for result in results[:5]:
        print(f"\n{result['segment_id']}:")
        print(f"  Speaker: {result['speaker']}")
        print(f"  Text: {result['text'][:80]}...")

    if len(results) > 5:
        print(f"\n... and {len(results) - 5} more segments")

    return results


if __name__ == "__main__":
    dialogue_to_voice()


# Test with example data
async def test_with_example():
    """Test the dialogue processing with example input"""

    example_dialogues = [
        "[rick] Alright Morty, you know how your computer runs multiple programs at once? Browser, music, whatever? That's concurrent execution, but here's the thing - with one CPU core, they're not actually running together. [morty] Wait, what? But I can see them all working at the same time, Rick. [rick] That's timeslicing, genius. The operating system switches between processes so fast it creates an illusion of parallel execution. Like a really fast juggler - only one ball in the air at a time, but it looks simultaneous. [morty] Oh, so it's like taking turns super quickly? [rick] Exactly. But when you have more processes than CPU cores, someone's gotta decide who goes next. That's the scheduling problem. [morty] So there's like a referee deciding which program gets to run? [rick] Bingo. That's the scheduler - it uses algorithms to figure out the order and timing. Pretty neat system for managing chaos, right?",
        "[rick] Alright Morty, every computer process does two things - it either crunches numbers using the CPU, or it waits around for files and printers. We call them compute-bound or I/O-bound.[morty] So like, some programs are just doing math while others are reading stuff?[rick] Exactly. And here's the kicker - different systems need different scheduling. Batch systems don't care about speed, interactive systems need quick responses for users, and real-time systems have deadlines or people die.[morty] Wait, people die?[rick] Figure of speech, Morty. Now, scheduling comes in two flavors - non-preemptive where processes politely give up control, or preemptive where the OS just yanks the CPU away after a timer goes off.[morty] Oh, so it's like either asking nicely or just taking it?[rick] Bingo. The OS picks which strategy based on what kind of system it's running. Different environments, different rules.",
        "[rick] Alright Morty, CPU scheduling is like managing a busy restaurant kitchen. First-Come First-Served is fair but dumb - if a huge order comes first, everyone waits forever. [morty] So like, shorter jobs should go first then? [rick] Exactly! Shortest Job First cuts average wait time, but long jobs might never get served. That's called starvation, Morty. [morty] Wait, what about when people need quick responses, like on their phones and stuff? [rick] Round Robin gives everyone a time slice - fair turns for interactive systems. Priority scheduling handles important stuff first, but again, low priority tasks can starve. [morty] Geez Rick, there's gotta be something better than all this starvation! [rick] Multi-Level Feedback Queues, Morty! They learn - start everything high priority, then demote the CPU hogs. Adapts automatically to whatever your system actually needs.",
    ]

    print("=" * 60)
    print("TESTING WITH EXAMPLE DIALOGUES")
    print("=" * 60)
    print(f"\nProcessing {len(example_dialogues)} example dialogues\n")

    # Create semaphore to limit concurrent API requests (max 3 at a time)
    semaphore = asyncio.Semaphore(3)

    # Collect all segments and create async tasks
    all_tasks = []

    for dialogue_index, dialogue in enumerate(example_dialogues, 1):
        print(f"\nDialogue {dialogue_index}:")
        print(f"{'='*60}")

        # Split dialogue by speaker
        segments = split_dialogue_by_speaker(dialogue)

        print(f"Found {len(segments)} speaker segments:")
        for i, seg in enumerate(segments, 1):
            print(f"  {i}. [{seg['speaker']}] {seg['text'][:60]}...")

        # Create async task for each segment
        for segment_index, segment in enumerate(segments, 1):
            task = process_dialogue_segment(
                segment,
                dialogue_index,
                segment_index,
                output_dir=str(OUTPUT_DIR),
                semaphore=semaphore,
            )
            all_tasks.append(task)

    print(f"\n{'='*60}")
    print(f"Processing {len(all_tasks)} segments concurrently...")
    print(f"{'='*60}\n")

    # Run all segments concurrently
    results = await asyncio.gather(*all_tasks)

    print(f"\n{'='*60}")
    print(f"All segments processed! Total: {len(results)}")
    print(f"{'='*60}")

    # Print summary
    print(f"\n\n{'='*60}")
    print("EXAMPLE TEST RESULTS")
    print(f"{'='*60}\n")

    rick_count = sum(1 for r in results if r["speaker"] == "rick")
    morty_count = sum(1 for r in results if r["speaker"] == "morty")

    print(f"Total segments: {len(results)}")
    print(f"Rick segments: {rick_count}")
    print(f"Morty segments: {morty_count}\n")

    print("All segments:")
    for result in results:
        print(f"\n{result['segment_id']}:")
        print(f"  Speaker: {result['speaker']}")
        print(f"  Text: {result['text']}")

    return results


def run_test():
    """Run the example test"""
    return asyncio.run(test_with_example())
