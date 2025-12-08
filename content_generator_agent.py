"""
Content Generator Agent using LangChain and OpenAI.
Generates images, videos, and captions for social media, runs compliance checks,
and publishes content to LinkedIn, Instagram, and Facebook.
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent

# Import all tools
from tools.image_generator import generate_image
from tools.video_generator import generate_video
from tools.caption_generator import generate_caption
from tools.policy_checker import check_policy_compliance
from tools.design_checker import check_design_compliance
from tools.social_publisher import publish_to_social_media
from config import get_current_config

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# SYSTEM PROMPT GENERATION
# =============================================================================

def get_system_prompt() -> str:
    """
    Generate the system prompt with current configuration.
    The prompt instructs the agent on how to use tools and follow workflows.
    """
    config = get_current_config()
    
    return f"""You are a creative AI assistant that generates and publishes social media content.

═══════════════════════════════════════════════════════════════════
                        YOUR CAPABILITIES
═══════════════════════════════════════════════════════════════════

1. 🖼️  generate_image - Create images with DALL-E 3 (follows brand guidelines)
2. 🎬 generate_video - Create videos with Sora-2 (follows brand guidelines)  
3. 📝 generate_caption - Write platform-optimized captions with hashtags
4. ✅ check_policy_compliance - Verify content follows policy guidelines
5. 🎨 check_design_compliance - Verify visuals follow design guidelines
6. 📱 publish_to_social_media - Post content to LinkedIn, Instagram, or Facebook

═══════════════════════════════════════════════════════════════════
                      CURRENT CONFIGURATION
═══════════════════════════════════════════════════════════════════

Target Platforms: {', '.join(config.target_platforms)}
Video: {config.video_duration}s, aspect ratio {config.video_aspect_ratio} ({config.video_resolution})
Image: {config.image_size}, quality {config.image_quality}
Captions: {config.enable_captions}, style {config.caption_style}
Auto Compliance Check: {config.auto_compliance_check}
Auto Publish: {config.auto_publish}

═══════════════════════════════════════════════════════════════════
                       WORKFLOW INSTRUCTIONS
═══════════════════════════════════════════════════════════════════

STEP 1: UNDERSTAND THE REQUEST
- Ask about the event, theme, or message
- Confirm which platforms the user wants to publish to
- The configured platforms are: {', '.join(config.target_platforms)}

STEP 2: GENERATE CONTENT
- Always pass the "platform" parameter to generate_image or generate_video
- The tools automatically apply brand guidelines during generation
- Use these settings:
  * Images: size={config.image_size}, quality={config.image_quality}
  * Videos: seconds={config.video_duration}, aspect_ratio={config.video_aspect_ratio}

STEP 3: COMPLIANCE CHECKS (if auto_compliance_check is True)
{"- After generating, run check_policy_compliance AND check_design_compliance" if config.auto_compliance_check else "- Skip compliance checks unless user asks"}
- Present any warnings or issues to the user

STEP 4: GENERATE CAPTION (if enabled)
{"- Generate a caption using the user's caption style preference: " + config.caption_style if config.enable_captions else "- Skip caption generation unless user asks"}

STEP 5: PUBLISH (if auto_publish is True OR user requests it)
{"- Automatically publish to: " + ', '.join(config.target_platforms) if config.auto_publish else "- Ask user for confirmation before publishing"}
- Use publish_to_social_media with:
  * platform: the target platform
  * content_path: the local file path from generation step
  * caption_prompt: brief description for caption generation
  * content_type: "image" or "video"

═══════════════════════════════════════════════════════════════════
                         IMPORTANT NOTES
═══════════════════════════════════════════════════════════════════

- Images and videos are saved locally in generated_content/ folder
- Use the local file path when publishing, NOT the URL
- Each platform has different requirements:
  * LinkedIn: Professional tone, max 5 hashtags
  * Instagram: Casual/vibrant, emojis OK, max 30 hashtags
  * Facebook: Conversational, community-focused, max 3 hashtags
- Always be creative and helpful
- If something fails, explain clearly and suggest alternatives
"""


# =============================================================================
# AGENT CREATION
# =============================================================================

def create_content_agent():
    """
    Create and return the content generation agent.
    Uses LangChain's create_agent with all available tools.
    """
    
    # List of all tools the agent can use
    tools = [
        generate_image, 
        generate_video, 
        generate_caption,
        check_policy_compliance,
        check_design_compliance,
        publish_to_social_media
    ]
    
    # Create the agent using LangChain
    agent = create_agent(
        model="openai:gpt-5",
        tools=tools,
        system_prompt=get_system_prompt(),
        debug=False
    )
    
    return agent


# =============================================================================
# AGENT WRAPPER CLASS
# =============================================================================

class ContentGeneratorAgent:
    """
    Wrapper class for the content generation agent.
    Maintains conversation history and provides easy-to-use interface.
    """
    
    def __init__(self):
        """Initialize the agent and empty chat history."""
        self.agent = create_content_agent()
        self.chat_history = []
    
    def chat(self, user_input: str) -> str:
        """
        Send a message to the agent and get a response.
        Maintains conversation history for context.
        """
        try:
            # Add user message to history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Invoke the agent with full message history
            response = self.agent.invoke({
                "messages": self.chat_history
            })
            
            # Extract the AI response from messages
            messages = response.get("messages", [])
            if messages:
                # Find the last AI message
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and hasattr(msg, 'type') and msg.type == "ai":
                        ai_response = msg.content
                        self.chat_history.append({"role": "assistant", "content": ai_response})
                        return ai_response
                
                # Fallback: get last message content
                last_msg = messages[-1]
                if hasattr(last_msg, 'content'):
                    ai_response = last_msg.content
                    self.chat_history.append({"role": "assistant", "content": ai_response})
                    return ai_response
            
            return "I couldn't generate a response. Please try again."
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reset_history(self):
        """Clear the conversation history."""
        self.chat_history = []
    
    def refresh_agent(self):
        """Recreate the agent with updated configuration."""
        self.agent = create_content_agent()


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def get_agent() -> ContentGeneratorAgent:
    """Get a new instance of the content generator agent."""
    return ContentGeneratorAgent()
