"""
Social Media Publisher Tool.
Unified tool for publishing content to LinkedIn, Instagram, and Facebook.
Wraps the platform-specific posting functions into a single agent-callable tool.
"""

import os
from pathlib import Path
from langchain.tools import tool

# Import the existing platform-specific posting functions
from tools.linkedin import post_linkedin_image, post_linkedin_video
from tools.instagram import post_to_instagram_local, generate_caption_with_llm as ig_caption
from tools.facebook import post_facebook_image, post_facebook_video


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_file_exists(file_path: str) -> bool:
    """Check if the file exists at the given path."""
    return os.path.exists(file_path)


def get_latest_generated_file(content_type: str) -> str:
    """
    Get the most recently generated file of the specified type.
    Useful when user says "post the image I just generated".
    
    Args:
        content_type: Either "image" or "video"
    
    Returns:
        Path to the most recent file, or empty string if none found.
    """
    if content_type == "image":
        folder = Path("generated_content/images")
        extensions = [".png", ".jpg", ".jpeg"]
    else:
        folder = Path("generated_content/videos")
        extensions = [".mp4", ".mov"]
    
    if not folder.exists():
        return ""
    
    # Find all matching files and sort by modification time
    files = []
    for ext in extensions:
        files.extend(folder.glob(f"*{ext}"))
    
    if not files:
        return ""
    
    # Return the most recent file
    latest = max(files, key=lambda f: f.stat().st_mtime)
    return str(latest.absolute())


# =============================================================================
# MAIN TOOL
# =============================================================================

@tool
def publish_to_social_media(
    platform: str,
    content_path: str,
    caption_prompt: str,
    content_type: str = "image",
    video_title: str = ""
) -> str:
    """
    Publish content (image or video) to a social media platform.
    
    Args:
        platform: Target platform - "linkedin", "instagram", or "facebook".
        content_path: Local file path to the image or video to publish.
                      Use the path from generate_image or generate_video output.
        caption_prompt: Brief description of the content for caption generation.
                        The platform-specific caption will be auto-generated.
        content_type: Either "image" or "video". Default is "image".
        video_title: Optional title for videos (used on LinkedIn and Facebook).
    
    Returns:
        Success message with post details, or error message if publishing fails.
    
    Example:
        publish_to_social_media(
            platform="linkedin",
            content_path="generated_content/images/image_linkedin_20241208.png",
            caption_prompt="Announcing our new AI product launch",
            content_type="image"
        )
    """
    try:
        # Normalize platform name
        platform = platform.lower().strip()
        content_type = content_type.lower().strip()
        
        # Validate platform
        valid_platforms = ["linkedin", "instagram", "facebook"]
        if platform not in valid_platforms:
            return f"❌ Invalid platform: {platform}. Must be one of: {', '.join(valid_platforms)}"
        
        # Validate content type
        if content_type not in ["image", "video"]:
            return f"❌ Invalid content_type: {content_type}. Must be 'image' or 'video'."
        
        # Check if file exists
        if not validate_file_exists(content_path):
            # Try to find the latest generated file
            latest = get_latest_generated_file(content_type)
            if latest:
                content_path = latest
            else:
                return f"❌ File not found: {content_path}"
        
        # =====================================================================
        # LINKEDIN PUBLISHING
        # =====================================================================
        if platform == "linkedin":
            if content_type == "image":
                result = post_linkedin_image(caption_prompt, content_path)
            else:
                title = video_title if video_title else "Video"
                result = post_linkedin_video(caption_prompt, content_path, title=title)
            
            return f"""✅ Published to LinkedIn!

📱 Platform: LinkedIn
📄 Content: {content_type.capitalize()}
📁 File: {content_path}
📝 Caption Prompt: {caption_prompt}

🔗 Post Details: {result}"""

        # =====================================================================
        # INSTAGRAM PUBLISHING
        # =====================================================================
        elif platform == "instagram":
            if content_type == "video":
                return "❌ Instagram video posting is not yet implemented. Only images are supported."
            
            # Generate caption using their caption function
            caption = ig_caption(caption_prompt)
            post_to_instagram_local(content_path, caption)
            
            return f"""✅ Published to Instagram!

📱 Platform: Instagram
📄 Content: {content_type.capitalize()}
📁 File: {content_path}
📝 Generated Caption: {caption}"""

        # =====================================================================
        # FACEBOOK PUBLISHING
        # =====================================================================
        elif platform == "facebook":
            if content_type == "image":
                result = post_facebook_image(caption_prompt, content_path)
            else:
                title = video_title if video_title else "Video"
                result = post_facebook_video(caption_prompt, content_path, title=title)
            
            return f"""✅ Published to Facebook!

📱 Platform: Facebook
📄 Content: {content_type.capitalize()}
📁 File: {content_path}
📝 Caption Prompt: {caption_prompt}

🔗 Post Details: {result}"""

    except FileNotFoundError as e:
        return f"❌ File not found: {str(e)}"
    except RuntimeError as e:
        return f"❌ Publishing failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
