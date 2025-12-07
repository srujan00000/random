"""
Content Generation Agent - CLI Entry Point
A conversational AI agent for generating social media content.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from config import get_config_from_user, set_current_config, get_current_config
from content_generator_agent import ContentGeneratorAgent


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🎨 CONTENT GENERATION AGENT                                     ║
║   ─────────────────────────────────────────────────────────────   ║
║   AI-Powered Social Media Content Creator                         ║
║                                                                   ║
║   Powered by: GPT-5 | DALL-E 3 | Sora                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print available commands."""
    help_text = """
┌─────────────────────────────────────────────────────────────────┐
│  Available Commands                                             │
├─────────────────────────────────────────────────────────────────┤
│  /config    - Reconfigure generation settings                  │
│  /settings  - View current settings                            │
│  /clear     - Clear conversation history                       │
│  /help      - Show this help message                           │
│  /exit      - Exit the application                             │
│  /quit      - Exit the application                             │
└─────────────────────────────────────────────────────────────────┘

💡 Tips:
   • Describe your event/theme and ask for content suggestions
   • Request specific platforms: "Create an Instagram post for..."
   • Ask for variations: "Give me 3 different styles for..."
   • Refine results: "Make it more professional" or "Add more energy"
"""
    print(help_text)


def check_api_key() -> bool:
    """Verify that the OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("\n❌ ERROR: OpenAI API key not configured!")
        print("\nPlease set your API key in the .env file:")
        print("  OPENAI_API_KEY=sk-your-actual-api-key-here")
        print("\nGet your API key from: https://platform.openai.com/api-keys")
        return False
    
    return True


def main():
    """Main entry point for the CLI application."""
    
    # Print banner
    print_banner()
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    print("✅ API key found!")
    
    # Get configuration from user
    print("\nLet's configure your content generation settings.")
    print("(Press Enter to accept default values)")
    
    config = get_config_from_user()
    set_current_config(config)
    
    # Initialize agent
    print("\n🚀 Initializing Content Generation Agent...")
    agent = ContentGeneratorAgent()
    print("✅ Agent ready!\n")
    
    # Print help
    print_help()
    
    # Main chat loop
    print("\n" + "=" * 65)
    print("  Start chatting! Tell me about your event or content needs.")
    print("=" * 65 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            # Skip empty input
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()
                
                if command in ["/exit", "/quit"]:
                    print("\n👋 Goodbye! Thanks for using Content Generation Agent.")
                    break
                
                elif command == "/help":
                    print_help()
                    continue
                
                elif command == "/config":
                    print("\n🔄 Reconfiguring settings...")
                    new_config = get_config_from_user()
                    set_current_config(new_config)
                    agent.refresh_agent()
                    print("✅ Agent updated with new configuration!")
                    continue
                
                elif command == "/settings":
                    print(get_current_config())
                    continue
                
                elif command == "/clear":
                    agent.reset_history()
                    print("✅ Conversation history cleared!")
                    continue
                
                else:
                    print(f"❓ Unknown command: {user_input}")
                    print("   Type /help to see available commands.")
                    continue
            
            # Send to agent and get response
            print("\n🤖 Agent: ", end="")
            print("-" * 55)
            
            response = agent.chat(user_input)
            print(response)
            
            print("-" * 55)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Content Generation Agent.")
            break
        
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("   Please try again or type /help for assistance.")


if __name__ == "__main__":
    main()
