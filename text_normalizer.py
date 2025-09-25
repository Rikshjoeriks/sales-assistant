#!/usr/bin/env python3
"""
Text Normalizer for Spec Matcher
Cleans and organizes automotive specification text for better GPT processing
"""

import re
import string
from openai import OpenAI

def basic_text_cleanup(text):
    """First pass: Basic cleanup of spacing, symbols, and formatting"""
    
    # Remove or replace problematic characters
    text = text.replace('\r\n', '\n').replace('\r', '\n')  # Normalize line endings
    text = text.replace('\t', ' ')  # Replace tabs with spaces
    text = re.sub(r'[^\w\s\-\(\)\[\].,;:!?\'"°%/&+]', ' ', text)  # Keep only readable chars
    
    # Fix spacing issues
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double newline
    text = re.sub(r'\n ', '\n', text)  # Remove space after newline
    text = re.sub(r' \n', '\n', text)  # Remove space before newline
    
    # Fix punctuation spacing
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([,.;:!?])([A-Za-z])', r'\1 \2', text)  # Add space after punctuation
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lowercase-uppercase
    
    # Fix parentheses and brackets
    text = re.sub(r'\s*\(\s*', ' (', text)
    text = re.sub(r'\s*\)\s*', ') ', text)
    text = re.sub(r'\s*\[\s*', ' [', text)
    text = re.sub(r'\s*\]\s*', '] ', text)
    
    # Clean up measurements and technical terms
    text = re.sub(r'(\d)\s*([A-Za-z]{1,3})\b', r'\1\2', text)  # "17 inch" -> "17inch"
    text = re.sub(r'(\d)\s*([°%])', r'\1\2', text)  # "90 %" -> "90%"
    
    # Remove excessive whitespace
    text = re.sub(r'[ ]{2,}', ' ', text)
    text = text.strip()
    
    return text

def intelligent_text_organization(text, llm_model="gpt-4o"):
    """Second pass: Use GPT to ONLY organize existing text without adding content"""
    
    # Don't process if text is already very clean and short
    if len(text) < 200 and text.count('\n') < 5:
        return text
    
    prompt = """You are a text organization expert for automotive specifications.

CRITICAL RULES:
1. NEVER add new words, information, or content that isn't in the original
2. NEVER complete incomplete sentences with new information
3. NEVER change technical terms, numbers, or specifications
4. ONLY reorganize existing text into cleaner paragraphs
5. ONLY fix obvious spacing and line break issues
6. If unsure, leave text unchanged

TASK: Reorganize this automotive text for better readability WITHOUT adding any new content.

INPUT TEXT:
{text}

OUTPUT: Same content, just better organized with proper spacing and paragraph breaks. NO NEW WORDS."""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=llm_model,
            temperature=0.1,  # Very low temperature for conservative changes
            messages=[{"role": "user", "content": prompt.format(text=text)}],
            stream=False
        )
        
        # Safely extract content from response
        try:
            organized_text = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as e:
            print(f"⚠️ Invalid API response structure: {e}, using basic cleanup only")
            return text
        
        # Strict validation - content should not grow significantly
        original_words = set(text.lower().split())
        organized_words = set(organized_text.lower().split()) if organized_text else set()
        
        # Check if too many new words were added
        new_words = organized_words - original_words
        if len(new_words) > len(original_words) * 0.1:  # More than 10% new words = suspicious
            print(f"⚠️ GPT organization added too many new words: {new_words}")
            return text
        
        # Check length growth
        if organized_text and len(organized_text) > len(text) * 1.2:  # More than 20% growth = suspicious
            print("⚠️ GPT organization added too much content, using original")
            return text
        
        return organized_text.strip() if organized_text else text
            
    except Exception as e:
        print(f"⚠️ GPT organization failed: {e}, using basic cleanup only")
        return text

def normalize_spec_text(text, use_gpt_organization=True, llm_model="gpt-4o"):
    """
    Complete text normalization pipeline
    
    Args:
        text: Raw specification text
        use_gpt_organization: Whether to use GPT for intelligent organization
        llm_model: Model to use for organization
    
    Returns:
        Cleaned and organized text
    """
    
    if not text or not text.strip():
        return text
    
    print("🧹 Normalizing input text...")
    
    # Step 1: Basic cleanup
    print("  📋 Basic cleanup (spacing, symbols, formatting)...")
    cleaned_text = basic_text_cleanup(text)
    
    # Step 2: Intelligent organization (optional)
    if use_gpt_organization and len(cleaned_text) > 100:
        print("  🤖 GPT organization (structuring, sentence completion)...")
        organized_text = intelligent_text_organization(cleaned_text, llm_model)
        
        # Final basic cleanup after GPT processing
        final_text = basic_text_cleanup(organized_text)
        
        print(f"  ✅ Normalized: {len(text)} → {len(final_text)} chars")
        return final_text
    else:
        print(f"  ✅ Basic cleanup: {len(text)} → {len(cleaned_text)} chars")
        return cleaned_text

def demo_normalizer():
    """Demo the text normalizer with sample automotive text"""
    
    # Sample messy automotive text
    sample_text = """LED    headlights with   adaptive  lighting
Heated  mirrors-electric   folding
All wheel drive(AWD)  system   available
17inch    steel wheels,Sakura
Automatic   air conditioning   system
12.3"touchscreen
Apple CarPlay®and   Wireless Android   Auto™
Safety:Driver  and passenger   airbags,side   and curtain   airbags
Emergency braking system   with   pedestrian
detection
Parking sensors-front   and rear
Cruise control with speed   limiter function"""

    print("🧪 Text Normalizer Demo")
    print("=" * 50)
    
    print("\n📝 Original Text:")
    print("-" * 30)
    print(sample_text)
    
    print(f"\nOriginal length: {len(sample_text)} characters")
    
    # Basic cleanup only
    basic_cleaned = basic_text_cleanup(sample_text)
    print(f"\n🔧 After Basic Cleanup ({len(basic_cleaned)} chars):")
    print("-" * 40)
    print(basic_cleaned)
    
    # Full normalization with GPT
    print(f"\n🤖 Running GPT Organization...")
    fully_normalized = normalize_spec_text(sample_text, use_gpt_organization=True)
    print(f"\n✨ After Full Normalization ({len(fully_normalized)} chars):")
    print("-" * 45)
    print(fully_normalized)

if __name__ == "__main__":
    demo_normalizer()
