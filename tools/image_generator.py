"""
Image Generation Tool using DALL-E 3.
Generates images based on text prompts for social media content.
"""

import os
from langchain.tools import tool
from openai import OpenAI


def get_client():
    """Get OpenAI client with lazy initialization."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
        str: URL of the generated image, or error message if generation fails.
    
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
        
        return f"""✅ Image Generated Successfully!

🖼️  Image URL: {image_url}

📝 DALL-E's Interpretation: {revised_prompt}

💡 Tip: Right-click and save the image, or use the URL directly in your social media post."""

    except Exception as e:
        return f"❌ Image generation failed: {str(e)}"
