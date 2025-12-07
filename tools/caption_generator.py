"""
Caption Generation Tool using GPT-5.
Generates captions with hashtags for social media platforms.
"""

import os
from langchain.tools import tool
from openai import OpenAI


def get_client():
    """Get OpenAI client with lazy initialization."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool
def generate_caption(
    content_description: str,
    platform: str = "instagram",
    style: str = "professional",
    include_hashtags: bool = True,
    include_emojis: bool = True
) -> str:
    """
    Generate a social media caption with relevant hashtags for the specified platform.
    
    Args:
        content_description: Description of the content (image/video) that needs a caption.
                            Include context about the event, product, or message.
        platform: Target social media platform. Options: "instagram", "linkedin", 
                  "twitter", "tiktok", "facebook". Default is "instagram".
        style: Caption tone/style. Options: "professional", "casual", "creative", 
               "humorous", "inspirational". Default is "professional".
        include_hashtags: Whether to include relevant hashtags. Default is True.
        include_emojis: Whether to include emojis in the caption. Default is True.
    
    Returns:
        str: Generated caption with hashtags, or error message if generation fails.
    """
    try:
        # Platform-specific guidelines
        platform_guidelines = {
            "instagram": {
                "max_length": 2200,
                "hashtag_count": "20-30",
                "notes": "Visual-first, storytelling works well, hashtags in comments or at end"
            },
            "linkedin": {
                "max_length": 3000,
                "hashtag_count": "3-5",
                "notes": "Professional tone, thought leadership, industry-specific hashtags"
            },
            "twitter": {
                "max_length": 280,
                "hashtag_count": "1-3",
                "notes": "Concise, punchy, trending hashtags work best"
            },
            "tiktok": {
                "max_length": 2200,
                "hashtag_count": "4-6",
                "notes": "Trendy, casual, include trending sounds/challenges references"
            },
            "facebook": {
                "max_length": 63206,
                "hashtag_count": "1-3",
                "notes": "Conversational, questions engage well, minimal hashtags"
            }
        }
        
        # Get platform info
        platform = platform.lower()
        if platform not in platform_guidelines:
            platform = "instagram"
        
        platform_info = platform_guidelines[platform]
        
        # Build the prompt for GPT-5
        system_prompt = f"""You are an expert social media content creator specializing in {platform}.
        
Your task is to create engaging captions that:
1. Match the {style} tone/style
2. Are optimized for {platform} (max {platform_info['max_length']} characters)
3. Include {platform_info['hashtag_count']} relevant, trending hashtags {"" if include_hashtags else "(SKIP hashtags as requested)"}
4. {"Include appropriate emojis" if include_emojis else "Do NOT include emojis"}
5. {platform_info['notes']}

Format your response as:
CAPTION:
[The main caption text]

{"HASHTAGS:" if include_hashtags else ""}
{"[Space-separated hashtags]" if include_hashtags else ""}
"""

        user_prompt = f"""Create a {style} caption for {platform} about:

{content_description}

Make it engaging and optimized for maximum reach and engagement."""

        # Get client and generate caption using GPT-5
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        generated_caption = response.choices[0].message.content
        
        return f"""✅ Caption Generated for {platform.upper()}!

{generated_caption}

📊 Platform Guidelines Applied:
   • Max Length: {platform_info['max_length']} chars
   • Recommended Hashtags: {platform_info['hashtag_count']}
   • Style: {style.capitalize()}"""

    except Exception as e:
        return f"❌ Caption generation failed: {str(e)}"
