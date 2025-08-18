#!/usr/bin/env python3
"""
Audio transcription tool using Gemini API
"""
import sys
import argparse
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple
from common import load_prompt, initialize_gemini_client, save_output

AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aiff', '.aac', '.ogg', '.flac']

def collect_audio_files(path: Path, recursive: bool = False, pattern: str = None) -> List[Path]:
    """
    Collect audio files from a directory.
    
    Args:
        path: Directory path to search
        recursive: Whether to search subdirectories
        pattern: Optional file pattern to match (e.g., '*.mp3')
    
    Returns:
        List of audio file paths
    """
    audio_files = []
    
    if recursive:
        for ext in AUDIO_EXTENSIONS:
            audio_files.extend(path.rglob(f'*{ext}'))
    else:
        for ext in AUDIO_EXTENSIONS:
            audio_files.extend(path.glob(f'*{ext}'))
    
    if pattern:
        audio_files = [f for f in audio_files if fnmatch.fnmatch(f.name, pattern)]
    
    return sorted(audio_files)

def transcribe_audio(audio_path: str, output_path: str = None, prompt_path: str = None):
    """
    Transcribe an audio file using the Gemini API.
    
    Args:
        audio_path: Path to the audio file (MP3, WAV, etc.)
        output_path: Optional path for the output transcript file
        prompt_path: Optional path to a custom prompt file
    """
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not audio_path.suffix.lower() in AUDIO_EXTENSIONS:
        raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
    
    # Check file size and warn if large
    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 20:
        print(f"⚠️  Warning: Large file detected ({file_size_mb:.1f} MB)")
        print("   Files over 20MB may fail or take a long time to process.")
        print("   Consider splitting the audio file into smaller segments.")
        print("   Attempting to process anyway...")
    
    if output_path is None:
        output_path = audio_path.parent / f"{audio_path.stem}_transcript.md"
    else:
        output_path = Path(output_path)
    
    client = initialize_gemini_client()
    
    print(f"Uploading audio file: {audio_path.name}...")
    try:
        audio_file = client.files.upload(file=str(audio_path))
        print(f"File uploaded successfully: {audio_file.name}")
    except Exception as e:
        raise Exception(f"Failed to upload audio file: {str(e)}")
    
    print("Generating transcript...")
    prompt = load_prompt(prompt_type='transcribe', custom_path=prompt_path)
    
    try:
        from google.genai import types
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=[prompt, audio_file],
            config=types.GenerateContentConfig(
                temperature=0.0,  # Deterministic output for maximum consistency
                top_p=0.95,       # Nucleus sampling for better quality
                top_k=40,         # Limit token selection for consistency
            )
        )
        
        # Check if response has text
        if not response or not response.text:
            raise Exception("Gemini API returned empty response. The audio file might be too long or unsupported.")
        
        transcript = response.text
        save_output(transcript, output_path)
        
        print(f"✓ Transcription completed successfully!")
        
    except Exception as e:
        raise Exception(f"Failed to generate transcript: {str(e)}")
    finally:
        try:
            client.files.delete(name=audio_file.name)
            print(f"Cleaned up uploaded file: {audio_file.name}")
        except Exception:
            pass

def process_multiple_files(audio_files: List[Path], output_dir: Optional[Path] = None, prompt_path: str = None) -> Tuple[int, int]:
    """
    Process multiple audio files.
    
    Args:
        audio_files: List of audio file paths
        output_dir: Optional directory to save all transcripts
        prompt_path: Optional custom prompt path
    
    Returns:
        Tuple of (successful_count, failed_count)
    """
    total = len(audio_files)
    successful = 0
    failed = 0
    failed_files = []
    
    print(f"\nFound {total} audio file(s) to process")
    print("=" * 50)
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{total}] Processing: {audio_file.name}")
        print("-" * 40)
        
        try:
            if output_dir:
                output_path = output_dir / f"{audio_file.stem}_transcript.md"
            else:
                output_path = None
            
            transcribe_audio(str(audio_file), str(output_path) if output_path else None, prompt_path)
            successful += 1
        except Exception as e:
            print(f"✗ Failed to process {audio_file.name}: {str(e)}")
            failed += 1
            failed_files.append((audio_file.name, str(e)))
    
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    print(f"✓ Successfully processed: {successful}/{total}")
    if failed > 0:
        print(f"✗ Failed: {failed}/{total}")
        print("\nFailed files:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    
    return successful, failed

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using the Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.mp3
  %(prog)s audio.mp3 -o transcript.txt
  %(prog)s /path/to/audio.wav --output /path/to/output.txt
  %(prog)s /path/to/audio_directory --recursive
  %(prog)s ./audio_files --pattern "*.mp3" --output-dir ./transcripts
  %(prog)s audio.mp3 --prompt custom_prompt.txt
        """
    )
    
    parser.add_argument(
        "input_path",
        help="Path to an audio file or directory containing audio files"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (for single file) or ignored for directory input",
        default=None
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for transcripts (when processing multiple files)",
        default=None
    )
    
    parser.add_argument(
        "-r", "--recursive",
        help="Process audio files in subdirectories recursively",
        action="store_true",
        default=False
    )
    
    parser.add_argument(
        "--pattern",
        help="File pattern to match (e.g., '*.mp3', 'interview_*.wav')",
        default=None
    )
    
    parser.add_argument(
        "--prompt",
        help="Path to a custom prompt file (default: use prompts/transcribe.txt)",
        default=None
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    if not input_path.exists():
        print(f"Error: Path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if input_path.is_file():
            if args.output_dir:
                print("Warning: --output-dir is ignored when processing a single file")
            transcribe_audio(str(input_path), args.output, args.prompt)
        elif input_path.is_dir():
            if args.output:
                print("Warning: --output is ignored when processing a directory")
            
            output_dir = None
            if args.output_dir:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            audio_files = collect_audio_files(input_path, args.recursive, args.pattern)
            
            if not audio_files:
                print(f"No audio files found in {input_path}")
                if not args.recursive:
                    print("Tip: Use --recursive to search in subdirectories")
                if args.pattern:
                    print(f"Pattern used: {args.pattern}")
                sys.exit(0)
            
            successful, failed = process_multiple_files(audio_files, output_dir, args.prompt)
            
            if failed > 0:
                sys.exit(1)
        else:
            print(f"Error: {input_path} is neither a file nor a directory", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()