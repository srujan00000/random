# Content Generation Agent 🎨

AI-powered social media content generator using GPT-5, DALL-E 3, and Sora.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your OpenAI API key to .env
OPENAI_API_KEY=sk-your-key-here

# 3. Run
python main.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                    (CLI Interface)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              content_generator_agent.py                     │
│         (LangChain Agent with GPT-5)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Image    │  │   Video    │  │  Caption   │
    │ Generator  │  │ Generator  │  │ Generator  │
    │ (DALL-E 3) │  │  (Sora)    │  │  (GPT-5)   │
    └────────────┘  └────────────┘  └────────────┘
```

## Tools

| Tool | Description | Model |
|------|-------------|-------|
| `generate_image` | Creates images from text prompts | DALL-E 3 |
| `generate_video` | Creates videos from text prompts | Sora |
| `generate_caption` | Writes platform-optimized captions with hashtags | GPT-5 |

## Configuration

The CLI prompts for these settings on startup:

- **Video Duration**: 5-60 seconds
- **Video Resolution**: 720p / 1080p / 4k
- **Aspect Ratio**: 16:9 / 9:16 / 1:1
- **Captions**: Enable/disable auto-caption generation
- **Caption Style**: professional / casual / creative
- **Image Size**: 1024x1024 / 1792x1024 / 1024x1792
- **Image Quality**: standard / hd

## CLI Commands

| Command | Description |
|---------|-------------|
| `/config` | Reconfigure settings |
| `/settings` | View current settings |
| `/clear` | Clear conversation history |
| `/help` | Show help |
| `/exit` | Exit application |

## Example Usage

```
🧑 You: I have a tech conference next week. Create content for it.

🤖 Agent: I'd be happy to help! Let me ask a few questions:
   1. What's the conference name and theme?
   2. Which platforms do you need content for?
   3. What's the key message or announcement?

🧑 You: It's called "AI Summit 2024", theme is future of AI, 
       need LinkedIn and Instagram. Announce our new product launch.

🤖 Agent: [Generates image + video + captions for both platforms]
```

## File Structure

```
content-generation-agent/
├── main.py                      # CLI entry point
├── content_generator_agent.py   # LangChain agent setup
├── config.py                    # Configuration management
├── tools/
│   ├── __init__.py
│   ├── image_generator.py       # DALL-E 3 tool
│   ├── video_generator.py       # Sora tool
│   └── caption_generator.py     # Caption + hashtag tool
├── .env                         # API keys (not committed)
├── requirements.txt
└── README.md
```

## Integration Notes

This agent is designed to be integrated into a larger portal. Key integration points:

- `ContentGeneratorAgent` class can be imported and used directly
- `config.py` allows programmatic configuration
- Tools can be imported individually from `tools/` module
