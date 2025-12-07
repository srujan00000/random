"""
Content Generator Agent using LangChain and OpenAI.
This agent can generate images, videos, and captions for social media content,
and run compliance checks against policy and design guidelines.
"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent

from tools.image_generator import generate_image
from tools.video_generator import generate_video
from tools.caption_generator import generate_caption
from tools.policy_checker import check_policy_compliance
from tools.design_checker import check_design_compliance
from config import get_current_config

# Load environment variables
load_dotenv()


def get_system_prompt() -> str:
    """Generate the system prompt with current configuration."""
    config = get_current_config()
    
    return f"""You are a creative AI assistant specialized in generating social media content for marketing campaigns.

Your capabilities:
1. 🖼️  IMAGE GENERATION: Create stunning images using DALL-E 3
2. 🎬 VIDEO GENERATION: Create engaging videos using Sora
3. 📝 CAPTION GENERATION: Write platform-optimized captions with hashtags
4. ✅ POLICY COMPLIANCE: Check content against policy guidelines
5. 🎨 DESIGN COMPLIANCE: Check visual content against design guidelines

Current Configuration:
- Video Duration: {config.video_duration} seconds
- Video Aspect Ratio: {config.video_aspect_ratio} ({config.video_resolution})
- Captions Enabled: {config.enable_captions}
- Caption Style: {config.caption_style}
- Image Size: {config.image_size}
- Image Quality: {config.image_quality}
- Auto Compliance Check: {config.auto_compliance_check}

Guidelines:
1. When asked to create content, first understand the theme, event, or message
2. Suggest creative ideas before generating if the user seems unsure
3. Use the configured settings when generating videos and images
4. {"IMPORTANT: After generating any image or video, AUTOMATICALLY run both check_policy_compliance and check_design_compliance on the generated content." if config.auto_compliance_check else "Only run compliance checks when explicitly asked."}
5. {"Always generate a caption after creating images/videos" if config.enable_captions else "Only generate captions when explicitly asked"}
6. Optimize hashtags for each platform (Instagram, LinkedIn, Twitter, etc.)
7. Be conversational and help refine ideas through dialogue

When generating content:
- For images: Use size={config.image_size} and quality={config.image_quality}
- For videos: Use aspect_ratio={config.video_aspect_ratio}, seconds={config.video_duration}
- For captions: Use style={config.caption_style}

COMPLIANCE WORKFLOW:
After generating content, if auto_compliance_check is enabled:
1. Call check_policy_compliance with the content description and caption
2. Call check_design_compliance with the content description and type
3. Present both compliance reports to the user
4. If there are any FAIL or WARNING items, suggest improvements

Always be creative, professional, and focused on creating engaging social media content."""


def create_content_agent():
    """Create and return the content generation agent."""
    
    # Define all tools including compliance checkers
    tools = [
        generate_image, 
        generate_video, 
        generate_caption,
        check_policy_compliance,
        check_design_compliance
    ]
    
    # Create the agent using the new LangChain API
    agent = create_agent(
        model="openai:gpt-5",
        tools=tools,
        system_prompt=get_system_prompt(),
        debug=False
    )
    
    return agent


class ContentGeneratorAgent:
    """Wrapper class for the content generation agent with conversation memory."""
    
    def __init__(self):
        self.agent = create_content_agent()
        self.chat_history = []
    
    def chat(self, user_input: str) -> str:
        """Send a message to the agent and get a response."""
        try:
            # Add user message to history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Invoke the agent with the full message history
            response = self.agent.invoke({
                "messages": self.chat_history
            })
            
            # Extract the last AI message from the response
            messages = response.get("messages", [])
            if messages:
                # Get the last AI message
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
            
            return "I apologize, but I couldn't generate a response. Please try again."
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reset_history(self):
        """Clear the conversation history."""
        self.chat_history = []
    
    def refresh_agent(self):
        """Recreate the agent with updated configuration."""
        self.agent = create_content_agent()


# Convenience function to get a ready-to-use agent
def get_agent() -> ContentGeneratorAgent:
    """Get a new instance of the content generator agent."""
    return ContentGeneratorAgent()
