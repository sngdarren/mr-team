import pdfplumber
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

### Converts PDF to segmented educational content using Claude API ###

# Load environment variables
load_dotenv()


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Iterate through all pages
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n"
                    text += page_text
                    
        return text
    
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
        return None
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None


def segment_content_with_claude(text, system_prompt):
    """
    Send extracted text to Claude API with the content splitter system prompt.
    
    Args:
        text: The extracted text from PDF
        system_prompt: The system context from content_splitter.txt
        
    Returns:
        The API response content (segmented educational content)
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        return None
    
    try:
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8096,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        
        return response.content[0].text
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return None


def process_all_pdfs_in_folder(folder_path, system_prompt_path):
    """
    Process all PDF files in a given folder and send to OpenAI API.
    
    Args:
        folder_path: Path to the folder containing PDF files
        system_prompt_path: Path to the content_splitter.txt file
        
    Returns:
        List of API outputs for each processed PDF
    """
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {folder_path}")
        return []
    
    # Read system prompt
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    except FileNotFoundError:
        print(f"Error: System prompt file not found at {system_prompt_path}")
        return []
    
    print(f"Found {len(pdf_files)} PDF file(s) to process\n")
    
    results = []
    
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*60}")
        
        extracted_text = extract_text_from_pdf(str(pdf_file))
        
        if extracted_text:
            print(f"✓ Text extracted ({len(extracted_text)} characters)")
            print(f"Sending to Claude API...")
            
            segmented_content = segment_content_with_claude(extracted_text, system_prompt)
            
            if segmented_content:
                results.append({
                    'pdf_name': pdf_file.name,
                    'segments': segmented_content
                })
                print(f"✓ Segmentation completed")
                print(f"\n{segmented_content}\n")
            else:
                print(f"✗ Failed to segment content")
        else:
            print(f"✗ Failed to extract text from {pdf_file.name}")
    
    print(f"\n{'='*60}")
    print(f"All PDF files processed! Total results: {len(results)}")
    print(f"{'='*60}")
    
    return results


def pdf_to_chunk():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    pdf_data_folder = script_dir.parent / "data" / "pdf_data"
    system_prompt_path = script_dir.parent / "prompts" / "content_splitter.txt"
    
    print(f"Looking for PDFs in: {pdf_data_folder}")
    print(f"System prompt: {system_prompt_path}")
    
    if not pdf_data_folder.exists():
        print(f"Error: Folder '{pdf_data_folder}' does not exist.")
        return
    
    if not system_prompt_path.exists():
        print(f"Error: System prompt file '{system_prompt_path}' does not exist.")
        return
    
    results = process_all_pdfs_in_folder(pdf_data_folder, system_prompt_path)
    
    print(f"\n\nFinal Results Summary:")
    print(f"{'='*60}")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['pdf_name']}")
        print(f"\n{result['segments']}\n")
        print(f"{'-'*60}")
    print(f"{'='*60}")
    
    return results


if __name__ == "__main__":
    pdf_to_chunk()