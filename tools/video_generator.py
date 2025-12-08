"""
Video Generation Tool using OpenAI Sora-2.
Generates videos following design and policy guidelines, saves locally.
"""

import os
from datetime import datetime
from pathlib import Path
from langchain.tools import tool
from openai import OpenAI


# =============================================================================
# CONFIGURATION: Aspect Ratio to Resolution Mapping
# =============================================================================

# Maps user-friendly aspect ratios to Sora API size parameters
# Each ratio is optimized for specific social media platforms
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
    }
}

# Platform to recommended aspect ratio mapping
PLATFORM_ASPECT_RATIO = {
    "linkedin": "16:9",
    "instagram": "1:1",
    "facebook": "16:9"
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client():
    """Get OpenAI client - created on first call to avoid import errors."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_output_dir() -> Path:
    """Create and return the output directory for generated videos."""
    output_dir = Path("generated_content/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_guidelines() -> str:
    """
    Load both design and policy guidelines to inject into the prompt.
    This ensures Sora generates content that follows our rules.
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
    This makes Sora aware of our brand standards.
    """
    guidelines = load_guidelines()
    
    # Platform-specific style hints
    platform_hints = {
        "linkedin": "professional, corporate, polished business aesthetic",
        "instagram": "vibrant, dynamic, visually striking, social media optimized",
        "facebook": "friendly, approachable, community-focused, engaging"
    }
    
    style_hint = platform_hints.get(platform.lower(), "professional, high-quality")
    
    # Build the enhanced prompt
    enhanced = f"""Create a video following these requirements:

USER REQUEST: {original_prompt}

STYLE: {style_hint}

MANDATORY GUIDELINES TO FOLLOW:
{guidelines}

IMPORTANT: The video must have a hook in the first 3 seconds, smooth transitions, 
stable footage, proper lighting, and no prohibited content. Ensure the visual style 
matches the target platform aesthetic."""

    return enhanced


def get_aspect_ratio_for_platform(platform: str) -> str:
    """Get the recommended aspect ratio for a given platform."""
    return PLATFORM_ASPECT_RATIO.get(platform.lower(), "16:9")


# =============================================================================
# MAIN TOOL
# =============================================================================

@tool
def generate_video(
    prompt: str,
    platform: str = "",
    aspect_ratio: str = "16:9",
    seconds: int = 10
) -> str:
    """
    Generate a video using Sora-2, following brand guidelines.
    
    Args:
        prompt: Description of the video to generate.
        platform: Target platform (linkedin, instagram, facebook) - affects style and aspect ratio.
        aspect_ratio: Video aspect ratio - "16:9", "9:16", "1:1", or "4:5".
                      If platform is specified, the optimal ratio is auto-selected.
        seconds: Video length in seconds (5-60).
    
    Returns:
        URL and local path of the generated video, plus generation details.
    """
    try:
        # Validate seconds (5-60 range)
        if not 5 <= seconds <= 60:
            seconds = 10
        
        # If platform specified, use its recommended aspect ratio
        if platform and platform.lower() in PLATFORM_ASPECT_RATIO:
            aspect_ratio = get_aspect_ratio_for_platform(platform)
        
        # Validate aspect ratio and get corresponding size
        if aspect_ratio not in ASPECT_RATIO_MAP:
            aspect_ratio = "16:9"
        
        size = ASPECT_RATIO_MAP[aspect_ratio]["size"]
        ratio_info = ASPECT_RATIO_MAP[aspect_ratio]
        
        # Enhance the prompt with our guidelines
        # This is the key part - we inject guidelines into Sora's prompt
        enhanced_prompt = enhance_prompt_with_guidelines(prompt, platform)
        
        # Generate video using Sora-2
        client = get_client()
        response = client.videos.create(
            model="sora-2",
            prompt=enhanced_prompt,
            size=size,
            seconds=seconds
        )
        
        video_url = response.data[0].url
        video_id = response.data[0].id
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        platform_tag = f"_{platform}" if platform else ""
        filename = f"video{platform_tag}_{timestamp}.mp4"
        
        # Attempt to download video locally
        output_dir = get_output_dir()
        local_path = output_dir / filename
        download_status = ""
        
        try:
            # Use the Sora API's download method
            video_content = client.videos.download_content(video_id)
            with open(local_path, 'wb') as f:
                f.write(video_content)
            download_status = f"💾 Local Path: {local_path.absolute()}"
        except Exception as download_error:
            download_status = f"⚠️  Local download failed: {str(download_error)}\n   Use the URL to download manually."
        
        return f"""✅ Video Generated Successfully!

🎬 Video URL: {video_url}

{download_status}

📱 Platform: {platform.upper() if platform else "General"}

📊 Video Details:
   • Duration: {seconds} seconds
   • Aspect Ratio: {aspect_ratio}
   • Resolution: {size}

🎯 Optimal Platforms for {aspect_ratio}: {', '.join(ratio_info['platforms'])}

✓ Generated following brand design and policy guidelines."""

    except Exception as e:
        return f"❌ Video generation failed: {str(e)}"
