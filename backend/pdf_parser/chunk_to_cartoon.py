import os
import json
import re
import asyncio
from pathlib import Path
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pdf_plumber import pdf_to_chunk

# Load environment variables
load_dotenv()


def split_dialogue_by_speaker(dialogue_text):
    """
    Split a dialogue string by [rick] and [morty] delimiters.
    
    Args:
        dialogue_text: String containing dialogue with [rick] and [morty] markers
        
    Returns:
        List of dicts: [{'speaker': 'rick', 'text': '...'}, ...]
    """
    pattern = r'\[(rick|morty)\]\s*'
    
    segments = []
    matches = list(re.finditer(pattern, dialogue_text, re.IGNORECASE))
    
    for i, match in enumerate(matches):
        speaker = match.group(1).lower()
        start = match.end()
        
        if i < len(matches) - 1:
            end = matches[i + 1].start()
        else:
            end = len(dialogue_text)
        
        text = dialogue_text[start:end].strip()
        
        if text:
            segments.append({
                'speaker': speaker,
                'text': text
            })
    
    return segments


async def convert_chunk_to_cartoon(chunk_text, system_prompt, segment_id):
    """
    Convert a text chunk to Rick and Morty style dialogue using Claude (async).
    
    Args:
        chunk_text: The educational text chunk to convert
        system_prompt: The system context from chunk_to_cartoon.txt
        segment_id: Identifier for this segment (for logging)
        
    Returns:
        The converted dialogue as a string
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return None
    
    try:
        client = AsyncAnthropic(api_key=api_key)
        
        print(f"  → Starting conversion for {segment_id}...")
        
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": chunk_text}
            ]
        )
        
        print(f"  ✓ Completed conversion for {segment_id}")
        return response.content[0].text
    
    except Exception as e:
        print(f"  ✗ Error calling Claude API for {segment_id}: {e}")
        return None


async def process_chunks_to_cartoons():
    """
    Process all PDF chunks and convert them to cartoon dialogues concurrently.
    
    Returns:
        List of cartoon dialogues for each PDF and segment
    """
    # Get the cartoon prompt
    script_dir = Path(__file__).parent
    cartoon_prompt_path = script_dir.parent / "prompts" / "chunk_to_cartoon.txt"
    
    if not cartoon_prompt_path.exists():
        print(f"Error: Cartoon prompt file '{cartoon_prompt_path}' does not exist.")
        return []
    
    try:
        with open(cartoon_prompt_path, 'r', encoding='utf-8') as f:
            cartoon_prompt = f.read()
    except Exception as e:
        print(f"Error reading cartoon prompt: {e}")
        return []
    
    # Get the chunks from pdf_to_chunk()
    print("Getting PDF chunks...\n")
    pdf_results = pdf_to_chunk()
    
    if not pdf_results:
        print("No PDF results to process")
        return []
    
    # Collect all segments to process concurrently
    all_tasks = []
    task_metadata = []
    
    for pdf_result in pdf_results:
        pdf_name = pdf_result['pdf_name']
        segments = pdf_result['segments']
        
        print(f"\n{'='*60}")
        print(f"Preparing segments from: {pdf_name}")
        print(f"{'='*60}")
        
        # Split the segments text into individual segments
        segment_blocks = segments.split('SEGMENT ')
        segment_blocks = [s.strip() for s in segment_blocks if s.strip()]
        
        for i, segment_block in enumerate(segment_blocks, 1):
            # Extract the script part (after "Script:")
            if 'Script:' in segment_block:
                script_start = segment_block.find('Script:') + len('Script:')
                segment_text = segment_block[script_start:].strip()
            else:
                segment_text = segment_block
            
            segment_id = f"{pdf_name} - Segment {i}"
            task = convert_chunk_to_cartoon(segment_text, cartoon_prompt, segment_id)
            all_tasks.append(task)
            task_metadata.append({
                'pdf_name': pdf_name,
                'segment_number': i,
                'original_text': segment_text
            })
    
    print(f"\n{'='*60}")
    print(f"Converting {len(all_tasks)} segments concurrently...")
    print(f"{'='*60}\n")
    
    # Run all conversions concurrently
    cartoon_dialogues = await asyncio.gather(*all_tasks)
    
    # Organize results by PDF
    cartoon_results = []
    current_pdf = None
    current_pdf_cartoons = None
    
    for metadata, dialogue in zip(task_metadata, cartoon_dialogues):
        if current_pdf != metadata['pdf_name']:
            if current_pdf_cartoons:
                cartoon_results.append(current_pdf_cartoons)
            current_pdf = metadata['pdf_name']
            current_pdf_cartoons = {
                'pdf_name': current_pdf,
                'cartoons': []
            }
        
        if dialogue:
            current_pdf_cartoons['cartoons'].append({
                'segment_number': metadata['segment_number'],
                'original_text': metadata['original_text'],
                'cartoon_dialogue': dialogue
            })
    
    if current_pdf_cartoons:
        cartoon_results.append(current_pdf_cartoons)
    
    print(f"\n{'='*60}")
    print(f"All segments converted! Total PDFs processed: {len(cartoon_results)}")
    print(f"{'='*60}")
    
    return cartoon_results


async def pdf_to_cartoon_chunk():
    """
    Process all PDF chunks and convert them to cartoon dialogues concurrently.
    Creates the skeleton JSON structure with transcripts and person fields.
    
    Returns:
        List of cartoon dialogue strings ready for async processing
    """
    results = await process_chunks_to_cartoons()
    
    # Extract just the cartoon dialogue strings into a flat list
    cartoon_dialogues = []
    
    for result in results:
        for cartoon in result['cartoons']:
            cartoon_dialogues.append(cartoon['cartoon_dialogue'])
    
    # Print final summary
    print(f"\n\n{'='*60}")
    print("FINAL CARTOON DIALOGUES SUMMARY")
    print(f"{'='*60}\n")
    print(f"Total cartoon dialogues: {len(cartoon_dialogues)}\n")
    
    for i, dialogue in enumerate(cartoon_dialogues, 1):
        print(f"--- Dialogue {i} ---")
        print(dialogue)
        print(f"\n{'-'*60}\n")
    
    # Create skeleton JSON structure with transcripts and person
    print(f"\n{'='*60}")
    print("CREATING METADATA SKELETON")
    print(f"{'='*60}\n")
    
    metadata = {
        "segment 1": {
            "transcripts": [],
            "person": [],
            "timestamps": [],
            "filename": []
        },
        "segment 2": {
            "transcripts": [],
            "person": [],
            "timestamps": [],
            "filename": []
        },
        "segment 3": {
            "transcripts": [],
            "person": [],
            "timestamps": [],
            "filename": []
        }
    }
    
    # Process each dialogue and populate transcripts and person
    for dialogue_index, dialogue in enumerate(cartoon_dialogues, 1):
        segment_key = f"segment {dialogue_index}"
        
        if segment_key in metadata:
            # Split dialogue by speaker
            segments = split_dialogue_by_speaker(dialogue)
            
            print(f"{segment_key.title()}: {len(segments)} speaker segments")
            
            for seg in segments:
                metadata[segment_key]["transcripts"].append(seg['text'])
                metadata[segment_key]["person"].append(seg['speaker'])
    
    # Save skeleton to JSON
    script_dir = Path(__file__).parent
    output_file = script_dir.parent / "data" / "audio_metadata.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved metadata skeleton to: {output_file}")
    print("  (timestamps and filename fields will be added by make_metadata.py)")
    
    return cartoon_dialogues


if __name__ == "__main__":
    pdf_to_cartoon_chunk()
