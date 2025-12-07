"""
Image Generation Tool using DALL-E 3.
Generates images based on text prompts and saves locally.
"""

import os
import requests
from datetime import datetime
from pathlib import Path
from langchain.tools import tool
from openai import OpenAI


def get_client():
    """Get OpenAI client with lazy initialization."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_output_dir() -> Path:
    """Get or create the output directory for generated content."""
    output_dir = Path("generated_content/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def download_image(url: str, filename: str) -> str:
    """Download image from URL and save locally."""
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


@tool
def generate_image(prompt: str, size: str = "1024x1024", quality: str = "hd") -> str:
    """
    Generate an image using DALL-E 3 based on the given prompt.
    
    Args:
        prompt: A detailed description of the image to generate. Be specific about 
                style, colors, composition, and mood for best results.
        size: Image dimensions. Options: "1024x1024", "1792x1024" (landscape), 
              "1024x1792" (portrait). Default is "1024x1024".
        quality: Image quality. Options: "standard" or "hd". Default is "hd".
    
    Returns:
        str: URL and local path of the generated image, or error message if generation fails.
    
    Example prompts for social media:
        - "Professional LinkedIn banner showing a modern tech conference with diverse attendees"
        - "Vibrant Instagram post for a summer sale with tropical colors and bold typography"
        - "Minimalist product showcase on white background with soft shadows"
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
        
        # Get client and generate image using DALL-E 3
        client = get_client()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        
        # Download and save locally
        local_path = download_image(image_url, filename)
        
        return f"""✅ Image Generated Successfully!

🖼️  Image URL: {image_url}

💾 Local Path: {local_path}

📝 DALL-E's Interpretation: {revised_prompt}

📐 Size: {size} | Quality: {quality}

💡 Tip: The image has been saved locally and can be accessed at the path above."""

    except Exception as e:
        return f"❌ Image generation failed: {str(e)}"
