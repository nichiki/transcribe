#!/usr/bin/env python3
"""
Text processing tool using Gemini API
Supports summarization, headline generation, and custom text processing tasks
"""
import sys
import argparse
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple
from common import load_prompt, initialize_gemini_client, generate_with_gemini, save_output

TEXT_EXTENSIONS = ['.txt', '.md', '.text']
TASK_TYPES = ['summarize', 'headline', 'custom']

def collect_text_files(path: Path, recursive: bool = False, pattern: str = None) -> List[Path]:
    """
    Collect text files from a directory.
    
    Args:
        path: Directory path to search
        recursive: Whether to search subdirectories
        pattern: Optional file pattern to match (e.g., '*.txt')
    
    Returns:
        List of text file paths
    """
    text_files = []
    
    if recursive:
        for ext in TEXT_EXTENSIONS:
            text_files.extend(path.rglob(f'*{ext}'))
    else:
        for ext in TEXT_EXTENSIONS:
            text_files.extend(path.glob(f'*{ext}'))
    
    if pattern:
        text_files = [f for f in text_files if fnmatch.fnmatch(f.name, pattern)]
    
    return sorted(text_files)

def process_text_file(text_path: str, output_path: str = None, task: str = 'summarize', prompt_path: str = None, rules_path: str = None):
    """
    Process a text file using the Gemini API.
    
    Args:
        text_path: Path to the text file
        output_path: Optional path for the output file
        task: Task type ('summarize', 'headline', or 'custom')
        prompt_path: Optional path to a custom prompt file
        rules_path: Optional path to a rules YAML file
    """
    text_path = Path(text_path)
    
    if not text_path.exists():
        raise FileNotFoundError(f"Text file not found: {text_path}")
    
    if not text_path.suffix.lower() in TEXT_EXTENSIONS:
        raise ValueError(f"Unsupported text format: {text_path.suffix}")
    
    # Check file size
    file_size_mb = text_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        print(f"⚠️  Warning: Large file detected ({file_size_mb:.1f} MB)")
        print("   Processing may take longer...")
    
    # Determine output path
    if output_path is None:
        suffix = f"_{task}" if task != 'custom' else "_processed"
        output_path = text_path.parent / f"{text_path.stem}{suffix}.md"
    else:
        output_path = Path(output_path)
    
    # Load the appropriate prompt
    if task == 'custom' and not prompt_path:
        raise ValueError("Custom task requires a prompt file (--prompt)")
    
    if prompt_path:
        prompt = load_prompt(custom_path=prompt_path, rules_path=rules_path)
    else:
        prompt = load_prompt(prompt_type=task, rules_path=rules_path)
    
    # Read the input text
    print(f"Reading text file: {text_path.name}...")
    text_content = text_path.read_text(encoding='utf-8')
    
    # Initialize Gemini and process
    client = initialize_gemini_client()
    
    try:
        result = generate_with_gemini(client, prompt, text_content)
        save_output(result, output_path)
        
        print(f"✓ {task.capitalize()} completed successfully!")
        print(f"✓ Output saved to: {output_path}")
        
    except Exception as e:
        raise Exception(f"Failed to process text: {str(e)}")

def process_multiple_files(text_files: List[Path], output_dir: Optional[Path], task: str, prompt_path: str = None, rules_path: str = None) -> Tuple[int, int]:
    """
    Process multiple text files.
    
    Args:
        text_files: List of text file paths
        output_dir: Optional directory to save all outputs
        task: Task type
        prompt_path: Optional custom prompt path
        rules_path: Optional rules YAML file path
    
    Returns:
        Tuple of (successful_count, failed_count)
    """
    total = len(text_files)
    successful = 0
    failed = 0
    failed_files = []
    
    print(f"\nFound {total} text file(s) to process")
    print(f"Task: {task}")
    print("=" * 50)
    
    for i, text_file in enumerate(text_files, 1):
        print(f"\n[{i}/{total}] Processing: {text_file.name}")
        print("-" * 40)
        
        try:
            if output_dir:
                suffix = f"_{task}" if task != 'custom' else "_processed"
                output_path = output_dir / f"{text_file.stem}{suffix}.md"
            else:
                output_path = None
            
            process_text_file(
                str(text_file), 
                str(output_path) if output_path else None,
                task,
                prompt_path,
                rules_path
            )
            successful += 1
        except Exception as e:
            print(f"✗ Failed to process {text_file.name}: {str(e)}")
            failed += 1
            failed_files.append((text_file.name, str(e)))
    
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
        description="Process text files using the Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize a single file
  %(prog)s document.txt --task summarize
  
  # Add headlines to a markdown file
  %(prog)s notes.md --task headline
  
  # Process with custom prompt
  %(prog)s report.txt --prompt my_analysis_prompt.txt
  
  # Process with writing rules
  %(prog)s document.txt --task summarize --rules rules/writing-rules.yaml
  
  # Process all text files in a directory
  %(prog)s /path/to/texts/ --task summarize --recursive
  
  # Process specific files with pattern
  %(prog)s ./documents/ --pattern "report_*.txt" --task summarize
  
  # Save outputs to specific directory
  %(prog)s ./inputs/ --task headline --output-dir ./outputs/
        """
    )
    
    parser.add_argument(
        "input_path",
        help="Path to a text file or directory containing text files"
    )
    
    parser.add_argument(
        "--task",
        choices=TASK_TYPES,
        default="summarize",
        help="Processing task type (default: summarize)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (for single file) or ignored for directory input",
        default=None
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for processed files (when processing multiple files)",
        default=None
    )
    
    parser.add_argument(
        "-r", "--recursive",
        help="Process text files in subdirectories recursively",
        action="store_true",
        default=False
    )
    
    parser.add_argument(
        "--pattern",
        help="File pattern to match (e.g., '*.txt', 'doc_*.md')",
        default=None
    )
    
    parser.add_argument(
        "--prompt",
        help="Path to a custom prompt file (required for 'custom' task)",
        default=None
    )
    
    parser.add_argument(
        "--rules",
        nargs='?',
        const="rules/writing-rules.yaml",
        help="Path to a YAML file containing writing rules (default: rules/writing-rules.yaml if flag is used without path)",
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
            process_text_file(str(input_path), args.output, args.task, args.prompt, args.rules)
        elif input_path.is_dir():
            if args.output:
                print("Warning: --output is ignored when processing a directory")
            
            output_dir = None
            if args.output_dir:
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
            
            text_files = collect_text_files(input_path, args.recursive, args.pattern)
            
            if not text_files:
                print(f"No text files found in {input_path}")
                print(f"Supported extensions: {', '.join(TEXT_EXTENSIONS)}")
                if not args.recursive:
                    print("Tip: Use --recursive to search in subdirectories")
                if args.pattern:
                    print(f"Pattern used: {args.pattern}")
                sys.exit(0)
            
            successful, failed = process_multiple_files(text_files, output_dir, args.task, args.prompt, args.rules)
            
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