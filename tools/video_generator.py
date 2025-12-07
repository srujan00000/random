"""
Video Generation Tool using OpenAI Sora.
Generates videos based on text prompts for social media content.
"""

import os
from langchain.tools import tool
from openai import OpenAI


def get_client():
    """Get OpenAI client with lazy initialization."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool
def generate_video(
    prompt: str, 
    duration: int = 10, 
    resolution: str = "1080p",
    aspect_ratio: str = "16:9"
) -> str:
    """
    Generate a video using OpenAI Sora based on the given prompt.
    
    Args:
        prompt: A detailed description of the video to generate. Include details about
                the scene, action, camera movement, lighting, and style for best results.
        duration: Video length in seconds (5-60). Default is 10 seconds.
        resolution: Video resolution. Options: "720p", "1080p", "4k". Default is "1080p".
        aspect_ratio: Video aspect ratio. Options: "16:9" (landscape/YouTube), 
                      "9:16" (portrait/TikTok/Reels), "1:1" (square/Instagram). 
                      Default is "16:9".
    
    Returns:
        str: URL of the generated video, or error message if generation fails.
    
    Example prompts for social media:
        - "Cinematic drone shot flying over a modern city skyline at sunset, golden hour lighting"
        - "Product reveal animation with sleek transitions and professional lighting"
        - "Behind-the-scenes office footage with natural movement and candid moments"
    """
    try:
        # Validate duration
        if not 5 <= duration <= 60:
            duration = 10
        
        # Validate resolution
        valid_resolutions = ["720p", "1080p", "4k"]
        if resolution not in valid_resolutions:
            resolution = "1080p"
        
        # Validate aspect ratio
        valid_ratios = ["16:9", "9:16", "1:1"]
        if aspect_ratio not in valid_ratios:
            aspect_ratio = "16:9"
        
        # Get client and generate video using Sora
        client = get_client()
        response = client.videos.generate(
            model="sora-1",
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            aspect_ratio=aspect_ratio
        )
        
        video_url = response.data[0].url
        
        return f"""✅ Video Generated Successfully!

🎬 Video URL: {video_url}

📊 Video Details:
   • Duration: {duration} seconds
   • Resolution: {resolution}
   • Aspect Ratio: {aspect_ratio}

💡 Platform Recommendations:
   • 16:9 → YouTube, LinkedIn, Twitter
   • 9:16 → TikTok, Instagram Reels, YouTube Shorts
   • 1:1 → Instagram Feed, Facebook"""

    except Exception as e:
        return f"❌ Video generation failed: {str(e)}"
