"""
Image Generation Tool using DALL-E 3.
Generates images following design and policy guidelines, saves locally.
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from langchain.tools import tool
from openai import OpenAI


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client():
    """Get OpenAI client - created on first call to avoid import errors."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_output_dir() -> Path:
    """Create and return the output directory for generated images."""
    output_dir = Path("generated_content/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_guidelines() -> str:
    """
    Load both design and policy guidelines to inject into the prompt.
    This ensures DALL-E generates content that follows our rules.
    """
    guidelines_dir = Path(__file__).parent.parent / "guidelines"
    
    combined = ""
    
    # Load design guidelines (for visual rules)
    design_path = guidelines_dir / "design_guidelines.md"
    if design_path.exists():
        with open(design_path, 'r', encoding='utf-8') as f:
            combined += "DESIGN RULES:\n" + f.read() + "\n\n"
    
    # Load policy guidelines (for content rules)
    policy_path = guidelines_dir / "policy_guidelines.md"
    if policy_path.exists():
        with open(policy_path, 'r', encoding='utf-8') as f:
            combined += "CONTENT POLICY:\n" + f.read()
    
    return combined


def enhance_prompt_with_guidelines(original_prompt: str, platform: str = "") -> str:
    """
    Enhance the user's prompt by adding guideline requirements.
    This makes DALL-E aware of our brand standards.
    """
    guidelines = load_guidelines()
    
    # Platform-specific style hints
    platform_hints = {
        "linkedin": "professional, corporate, clean aesthetic",
        "instagram": "vibrant, eye-catching, social media optimized",
        "facebook": "friendly, approachable, community-focused"
    }
    
    style_hint = platform_hints.get(platform.lower(), "professional, high-quality")
    
    # Build the enhanced prompt
    enhanced = f"""Create an image following these requirements:

USER REQUEST: {original_prompt}

STYLE: {style_hint}

MANDATORY GUIDELINES TO FOLLOW:
{guidelines}

IMPORTANT: The image must be professional, high-quality (1080p+), with proper composition 
(rule of thirds), good lighting, and no prohibited content. Ensure the visual style matches 
the target platform aesthetic."""

    return enhanced


def download_image(url: str, filename: str) -> str:
    """Download image from URL and save to local directory."""
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        output_dir = get_output_dir()
        filepath = output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return str(filepath.absolute())
    except Exception as e:
        return f"Download failed: {str(e)}"


# =============================================================================
# MAIN TOOL
# =============================================================================

@tool
def generate_image(
    prompt: str, 
    platform: str = "",
    size: str = "1024x1024", 
    quality: str = "hd"
) -> str:
    """
    Generate an image using DALL-E 3, following brand guidelines.
    
    Args:
        prompt: Description of the image to generate.
        platform: Target platform (linkedin, instagram, facebook) - affects style.
        size: Image dimensions - "1024x1024", "1792x1024" (landscape), "1024x1792" (portrait).
        quality: Image quality - "standard" or "hd".
    
    Returns:
        URL and local path of the generated image, plus generation details.
    """
    try:
        # Validate size parameter
        valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
        if size not in valid_sizes:
            size = "1024x1024"
        
        # Validate quality parameter
        valid_qualities = ["standard", "hd"]
        if quality not in valid_qualities:
            quality = "hd"
        
        # Enhance the prompt with our guidelines
        # This is the key part - we inject guidelines into DALL-E's prompt
        enhanced_prompt = enhance_prompt_with_guidelines(prompt, platform)
        
        # Generate image using DALL-E 3
        client = get_client()
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_tag = f"_{platform}" if platform else ""
        filename = f"image{platform_tag}_{timestamp}.png"
        
        # Download and save locally
        local_path = download_image(image_url, filename)
        
        return f"""✅ Image Generated Successfully!

🖼️  Image URL: {image_url}

💾 Local Path: {local_path}

📱 Platform: {platform.upper() if platform else "General"}

📐 Size: {size} | Quality: {quality}

📝 DALL-E Interpretation: {revised_prompt}

✓ Generated following brand design and policy guidelines."""

    except Exception as e:
        return f"❌ Image generation failed: {str(e)}"
