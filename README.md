# Content Generation Agent 🎨

AI-powered social media content generator with publishing to LinkedIn, Instagram, and Facebook.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add API keys to .env (copy from .env.example)
OPENAI_API_KEY=sk-...
META_ACCESS_TOKEN=...   # For Facebook/Instagram
LINKEDIN_ACCESS_TOKEN=... # For LinkedIn

# 3. Run
python main.py
```

## Features

| Feature | Description |
|---------|-------------|
| **Image Generation** | DALL-E 3 with brand guidelines |
| **Video Generation** | Sora-2 with platform optimization |
| **Caption Generation** | Platform-specific with hashtags |
| **Compliance Checks** | Policy + Design validation |
| **Social Publishing** | LinkedIn, Instagram, Facebook |

## Workflow

```
1. Select platforms → 2. Generate content → 3. Compliance check → 4. Publish
```

The agent:
1. Asks which platforms to publish to (LinkedIn, Instagram, Facebook)
2. Generates image/video following brand guidelines
3. Runs compliance checks automatically
4. Publishes to selected platforms

## Configuration

On startup, you'll configure:
- **Target Platforms**: linkedin, instagram, facebook (multiple OK)
- **Video Duration**: 5-60 seconds
- **Aspect Ratio**: 16:9, 9:16, 1:1, 4:5
- **Auto-Compliance**: Run checks after generation
- **Auto-Publish**: Publish immediately or ask first

## CLI Commands

| Command | Action |
|---------|--------|
| `/config` | Reconfigure settings |
| `/settings` | View current config |
| `/clear` | Clear chat history |
| `/exit` | Exit |

## File Structure

```
├── main.py                      # CLI entry
├── content_generator_agent.py   # LangChain agent
├── config.py                    # Configuration
├── tools/
│   ├── image_generator.py       # DALL-E 3 + guidelines
│   ├── video_generator.py       # Sora-2 + guidelines
│   ├── caption_generator.py     # Captions + hashtags
│   ├── policy_checker.py        # Policy compliance
│   ├── design_checker.py        # Design compliance
│   ├── social_publisher.py      # Unified publisher
│   ├── linkedin.py              # LinkedIn API
│   ├── instagram.py             # Instagram API
│   └── facebook.py              # Facebook API
├── guidelines/
│   ├── policy_guidelines.md
│   └── design_guidelines.md
├── generated_content/           # Output folder
├── .env                         # API keys
└── .env.example                 # Template
```

## Environment Variables

```
OPENAI_API_KEY          # Required
META_ACCESS_TOKEN       # For Facebook/Instagram
FB_PAGE_ID              # Facebook Page ID
IG_USER_ID              # Instagram User ID
LINKEDIN_ACCESS_TOKEN   # LinkedIn OAuth token
LINKEDIN_URN            # LinkedIn person URN
```
