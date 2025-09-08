#!/usr/bin/env python3
"""
Common utilities for Gemini API processing
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def load_rules(rules_path: Optional[str] = None) -> Optional[str]:
    """
    Load writing rules from a YAML file and format them for prompt inclusion.
    
    Args:
        rules_path: Optional path to a rules YAML file
    
    Returns:
        Formatted rules text or None if no rules file specified
    """
    if not rules_path:
        return None
    
    rules_file = Path(rules_path)
    if not rules_file.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    
    print(f"Loading writing rules from: {rules_path}")
    
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules_data = yaml.safe_load(f)
    
    if not rules_data:
        return None
    
    # Format rules for prompt
    rules_text = "\n=== 表記ルール ===\n"
    rules_text += "以下の表記ルールに従って処理してください:\n\n"
    
    for rule in rules_data:
        rule_id = rule.get('id', '')
        judgement = rule.get('判定', '')
        correct = rule.get('正解', '')
        ng = rule.get('NG例', '')
        condition = rule.get('条件', '')
        example = rule.get('文章例', '')
        note = rule.get('備考', '')
        
        rules_text += f"【ルール {rule_id}】\n"
        if judgement:
            rules_text += f"  判定: {judgement}\n"
        if correct:
            rules_text += f"  正しい表記: {correct}\n"
        if ng:
            rules_text += f"  誤った表記: {ng}\n"
        if condition:
            rules_text += f"  条件: {condition}\n"
        if example:
            rules_text += f"  例: {example}\n"
        if note:
            rules_text += f"  備考: {note}\n"
        rules_text += "\n"
    
    rules_text += "=== 表記ルール終了 ===\n\n"
    return rules_text

def load_prompt(prompt_type: str = None, custom_path: Optional[str] = None, rules_path: Optional[str] = None) -> str:
    """
    Load prompt from a file, optionally with writing rules.
    
    Args:
        prompt_type: Type of prompt ('transcribe', 'summarize', 'headline')
        custom_path: Optional path to a custom prompt file
        rules_path: Optional path to a rules YAML file
    
    Returns:
        The prompt text, potentially with rules prepended
    """
    # Load base prompt
    base_prompt = ""
    if custom_path:
        prompt_file = Path(custom_path)
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {custom_path}")
        print(f"Using custom prompt from: {custom_path}")
        base_prompt = prompt_file.read_text(encoding='utf-8')
    elif prompt_type:
        prompt_file = Path(__file__).parent / "prompts" / f"{prompt_type}.txt"
        if prompt_file.exists():
            print(f"Using {prompt_type} prompt from: prompts/{prompt_type}.txt")
            base_prompt = prompt_file.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"Default prompt not found: prompts/{prompt_type}.txt")
    else:
        raise ValueError("Either prompt_type or custom_path must be specified")
    
    # Load and prepend rules if specified
    if rules_path:
        rules_text = load_rules(rules_path)
        if rules_text:
            return rules_text + base_prompt
    
    return base_prompt

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