#!/usr/bin/env python3
"""
Common utilities for Gemini API processing
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def load_prompt(prompt_type: str = None, custom_path: Optional[str] = None) -> str:
    """
    Load prompt from a file.
    
    Args:
        prompt_type: Type of prompt ('transcribe', 'summarize', 'headline')
        custom_path: Optional path to a custom prompt file
    
    Returns:
        The prompt text
    """
    if custom_path:
        prompt_file = Path(custom_path)
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {custom_path}")
        print(f"Using custom prompt from: {custom_path}")
        return prompt_file.read_text(encoding='utf-8')
    
    if prompt_type:
        prompt_file = Path(__file__).parent / "prompts" / f"{prompt_type}.txt"
        if prompt_file.exists():
            print(f"Using {prompt_type} prompt from: prompts/{prompt_type}.txt")
            return prompt_file.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"Default prompt not found: prompts/{prompt_type}.txt")
    
    raise ValueError("Either prompt_type or custom_path must be specified")

def initialize_gemini_client():
    """
    Initialize and return a Gemini API client.
    
    Returns:
        Initialized Gemini client
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise ValueError("Please set your GEMINI_API_KEY in the .env file")
    
    print(f"Initializing Gemini client...")
    return genai.Client(api_key=api_key)

def generate_with_gemini(client, prompt: str, content, config: Optional[types.GenerateContentConfig] = None):
    """
    Generate content using Gemini API.
    
    Args:
        client: Gemini client instance
        prompt: The prompt text
        content: The content to process (file object or text)
        config: Optional generation config
    
    Returns:
        Generated text response
    """
    if config is None:
        config = types.GenerateContentConfig(
            temperature=0.0,  # Deterministic output for maximum consistency
            top_p=0.95,       # Nucleus sampling for better quality
            top_k=40,         # Limit token selection for consistency
        )
    
    print("Generating content...")
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[prompt, content],
        config=config
    )
    
    if not response or not response.text:
        raise Exception("Gemini API returned empty response")
    
    return response.text

def save_output(content: str, output_path: Path, preview_length: int = 500):
    """
    Save content to a file and show preview.
    
    Args:
        content: Text content to save
        output_path: Path to save the file
        preview_length: Length of preview to show
    """
    print(f"Saving output to: {output_path}")
    output_path.write_text(content, encoding='utf-8')
    
    print(f"✓ Output saved successfully!")
    
    if preview_length > 0:
        print(f"\nPreview (first {preview_length} characters):")
        print("-" * 50)
        print(content[:preview_length] + ("..." if len(content) > preview_length else ""))
        print("-" * 50)