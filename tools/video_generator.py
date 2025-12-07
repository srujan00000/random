"""
Video Generation Tool using OpenAI Sora.
Generates videos based on text prompts and saves locally.
"""

import os
from datetime import datetime
from pathlib import Path
from langchain.tools import tool
from openai import OpenAI


def get_client():
    """Get OpenAI client with lazy initialization."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_output_dir() -> Path:
    """Get or create the output directory for generated content."""
    output_dir = Path("generated_content/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# Aspect ratio to resolution mapping for popular social media platforms
# Using resolutions that conform to Sora API and social media standards
ASPECT_RATIO_MAP = {
    "16:9": {
        "size": "1920x1080",
        "description": "Landscape - YouTube, LinkedIn, Twitter",
        "platforms": ["YouTube", "LinkedIn", "Twitter", "Facebook"]
    },
    "9:16": {
        "size": "1080x1920",
        "description": "Portrait - TikTok, Instagram Reels, YouTube Shorts",
        "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts", "Snapchat"]
    },
    "1:1": {
        "size": "1080x1080",
        "description": "Square - Instagram Feed, Facebook",
        "platforms": ["Instagram Feed", "Facebook", "LinkedIn"]
    },
    "4:5": {
        "size": "1080x1350",
        "description": "Portrait (4:5) - Instagram Feed optimal",
        "platforms": ["Instagram Feed", "Facebook"]
    },
    "21:9": {
        "size": "2560x1080",
        "description": "Ultra-wide - Cinematic content",
        "platforms": ["YouTube", "Cinematic"]
    }
}


def get_aspect_ratio_options() -> str:
    """Return formatted string of available aspect ratio options."""
    options = []
    for ratio, info in ASPECT_RATIO_MAP.items():
        options.append(f"  • {ratio} ({info['size']}) - {info['description']}")
    return "\n".join(options)


@tool
def generate_video(
    prompt: str, 
    aspect_ratio: str = "16:9",
    seconds: int = 10
) -> str:
    """
    Generate a video using OpenAI Sora based on the given prompt.
    
    Args:
        prompt: A detailed description of the video to generate. Include details about
                the scene, action, camera movement, lighting, and style for best results.
        aspect_ratio: Video aspect ratio. Options:
                      - "16:9" (1920x1080) - YouTube, LinkedIn, Twitter
                      - "9:16" (1080x1920) - TikTok, Reels, Shorts
                      - "1:1" (1080x1080) - Instagram/Facebook square
                      - "4:5" (1080x1350) - Instagram Feed optimal
                      - "21:9" (2560x1080) - Cinematic ultra-wide
                      Default is "16:9".
        seconds: Video length in seconds (5-60). Default is 10 seconds.
    
    Returns:
        str: URL and local path of the generated video, or error message if generation fails.
    
    Example prompts for social media:
        - "Cinematic drone shot flying over a modern city skyline at sunset, golden hour lighting"
        - "Product reveal animation with sleek transitions and professional lighting"
        - "Behind-the-scenes office footage with natural movement and candid moments"
    """
    try:
        # Validate seconds
        if not 5 <= seconds <= 60:
            seconds = 10
        
        # Get resolution from aspect ratio
        if aspect_ratio not in ASPECT_RATIO_MAP:
            aspect_ratio = "16:9"
        
        size = ASPECT_RATIO_MAP[aspect_ratio]["size"]
        ratio_info = ASPECT_RATIO_MAP[aspect_ratio]
        
        # Get client and generate video using Sora
        client = get_client()
        response = client.videos.create(
            model="sora-2",
            prompt=prompt,
            size=size,
            seconds=seconds
        )
        
        video_url = response.data[0].url
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}.mp4"
        
        # Download video using the API's download method
        output_dir = get_output_dir()
        local_path = output_dir / filename
        
        try:
            # Use the videos.download_content method
            video_content = client.videos.download_content(response.data[0].id)
            with open(local_path, 'wb') as f:
                f.write(video_content)
            download_status = f"💾 Local Path: {local_path.absolute()}"
        except Exception as download_error:
            download_status = f"⚠️  Local download failed: {str(download_error)}\n   Use the URL to download manually."
        
        return f"""✅ Video Generated Successfully!

🎬 Video URL: {video_url}

{download_status}

📊 Video Details:
   • Duration: {seconds} seconds
   • Aspect Ratio: {aspect_ratio}
   • Resolution: {size}

🎯 Recommended Platforms:
   {', '.join(ratio_info['platforms'])}

💡 Platform Recommendations:
   • 16:9 → YouTube, LinkedIn, Twitter
   • 9:16 → TikTok, Instagram Reels, YouTube Shorts
   • 1:1 → Instagram Feed, Facebook
   • 4:5 → Instagram Feed (optimal engagement)
   • 21:9 → Cinematic content"""

    except Exception as e:
        return f"❌ Video generation failed: {str(e)}"
