# Content Generation Agent 🎨

AI-powered social media content generator using GPT-5, DALL-E 3, and Sora-2.

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
     ┌─────────┬───────────┼───────────┬─────────┐
     ▼         ▼           ▼           ▼         ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│  Image  ││  Video  ││ Caption ││ Policy  ││ Design  │
│Generator││Generator││Generator││ Checker ││ Checker │
│(DALL-E 3)│(Sora-2) ││ (GPT-5) ││ (GPT-5) ││ (GPT-5) │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

## Tools

| Tool | Description | Model |
|------|-------------|-------|
| `generate_image` | Creates images, saves locally + URL | DALL-E 3 |
| `generate_video` | Creates videos with aspect ratio mapping | Sora-2 |
| `generate_caption` | Platform-optimized captions + hashtags | GPT-5 |
| `check_policy_compliance` | Reviews content against policy guidelines | GPT-5 |
| `check_design_compliance` | Reviews visuals against design guidelines | GPT-5 |

## Aspect Ratio Options

| Ratio | Resolution | Best For |
|-------|------------|----------|
| 16:9 | 1920x1080 | YouTube, LinkedIn, Twitter |
| 9:16 | 1080x1920 | TikTok, Reels, Shorts |
| 1:1 | 1080x1080 | Instagram Feed, Facebook |
| 4:5 | 1080x1350 | Instagram Feed (optimal) |
| 21:9 | 2560x1080 | Cinematic content |

## Configuration

The CLI prompts for these settings on startup:

- **Video Duration**: 5-60 seconds
- **Aspect Ratio**: 16:9 / 9:16 / 1:1 / 4:5 / 21:9 (with resolution)
- **Captions**: Enable/disable auto-caption generation
- **Caption Style**: professional / casual / creative
- **Image Size**: 1024x1024 / 1792x1024 / 1024x1792
- **Image Quality**: standard / hd
- **Auto Compliance**: Enable/disable automatic compliance checks

## CLI Commands

| Command | Description |
|---------|-------------|
| `/config` | Reconfigure settings |
| `/settings` | View current settings |
| `/clear` | Clear conversation history |
| `/help` | Show help |
| `/exit` | Exit application |

## Compliance Checking

The agent includes two compliance checkers:

### Policy Compliance (`guidelines/policy_guidelines.md`)
- Checks for prohibited content
- Validates brand voice and tone
- Ensures platform-specific compliance
- Verifies legal disclosures

### Design Compliance (`guidelines/design_guidelines.md`)
- Validates color and branding
- Checks composition and framing
- Verifies technical quality
- Ensures accessibility

When `auto_compliance_check` is enabled, both checks run automatically after content generation.

## Output

Generated content is saved to:
```
generated_content/
├── images/     # DALL-E 3 generated images
└── videos/     # Sora-2 generated videos
```

## File Structure

```
content-generation-agent/
├── main.py                      # CLI entry point
├── content_generator_agent.py   # LangChain agent setup
├── config.py                    # Configuration management
├── tools/
│   ├── __init__.py
│   ├── image_generator.py       # DALL-E 3 + local save
│   ├── video_generator.py       # Sora-2 + aspect ratios
│   ├── caption_generator.py     # Captions + hashtags
│   ├── policy_checker.py        # Policy compliance agent
│   └── design_checker.py        # Design compliance agent
├── guidelines/
│   ├── policy_guidelines.md     # Policy rules
│   └── design_guidelines.md     # Design rules
├── generated_content/           # Output folder (auto-created)
├── .env                         # API keys
├── requirements.txt
└── README.md
```

## Zero Data Retention Note

If you encounter a "zero data retention" error with Sora API, you need to contact OpenAI sales team to request ZDR approval for your organization. This is not a code workaround - it's a policy setting that must be enabled by OpenAI for your account.

## Integration Notes

This agent is designed to be integrated into a larger portal. Key integration points:

- `ContentGeneratorAgent` class can be imported and used directly
- `config.py` allows programmatic configuration
- Tools can be imported individually from `tools/` module
- Compliance checkers can be run standalone
