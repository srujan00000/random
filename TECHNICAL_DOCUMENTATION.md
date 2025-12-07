# Technical Documentation: Content Generation Agent

## Overview

This is a **LangChain-based AI agent** that generates social media content (images, videos, captions) using OpenAI's APIs and validates them against compliance guidelines. The agent uses a **tool-calling architecture** where GPT-5 orchestrates multiple specialized tools.

---

## Architecture

```
User Input (CLI)
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                     main.py (Entry Point)                    │
│  - Loads environment variables (.env)                        │
│  - Prompts user for configuration via config.py              │
│  - Initializes ContentGeneratorAgent                         │
│  - Runs interactive chat loop with command parsing           │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│            content_generator_agent.py (Agent Core)           │
│  - Uses langchain.agents.create_agent()                      │
│  - Model: "openai:gpt-5"                                     │
│  - Injects system prompt with current config                 │
│  - Registers 5 tools for the agent to call                   │
│  - Maintains conversation history for context                │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    Tool Execution Layer                      │
├──────────────────────────────────────────────────────────────┤
│  generate_image    │ DALL-E 3 API → downloads → local file  │
│  generate_video    │ Sora-2 API → downloads → local file    │
│  generate_caption  │ GPT-5 chat completion → formatted text │
│  check_policy      │ GPT-5 + guidelines → compliance report │
│  check_design      │ GPT-5 + guidelines → design report     │
└──────────────────────────────────────────────────────────────┘
```

---

## Module Breakdown

### 1. `main.py` - CLI Entry Point

**Purpose**: Interactive terminal interface for the agent.

**Key Functions**:
- `print_banner()`: Displays ASCII art header
- `check_api_key()`: Validates `OPENAI_API_KEY` exists in environment
- `main()`: Core loop that:
  1. Calls `get_config_from_user()` to collect settings
  2. Instantiates `ContentGeneratorAgent`
  3. Loops on `input()`, parsing commands (`/config`, `/exit`, etc.)
  4. Passes user messages to `agent.chat(user_input)`

**Command Handling**:
```
/config   → Re-run get_config_from_user(), refresh agent
/settings → Print current GenerationConfig
/clear    → Reset chat_history to []
/exit     → Break loop, exit program
```

---

### 2. `config.py` - Configuration Management

**Purpose**: Dataclass-based configuration with interactive prompts.

**Key Components**:

```python
ASPECT_RATIO_OPTIONS = {
    "16:9": {"size": "1920x1080", "desc": "..."},
    "9:16": {"size": "1080x1920", "desc": "..."},
    # Maps user-friendly ratio → Sora API size parameter
}

@dataclass
class GenerationConfig:
    video_duration: int = 10        # Sora seconds parameter
    video_aspect_ratio: str = "16:9" # Key into ASPECT_RATIO_OPTIONS
    enable_captions: bool = True
    caption_style: str = "professional"
    image_size: str = "1024x1024"   # DALL-E size parameter
    image_quality: str = "hd"       # DALL-E quality parameter
    auto_compliance_check: bool = True
    
    @property
    def video_resolution(self) -> str:
        # Derives resolution from aspect_ratio lookup
        return ASPECT_RATIO_OPTIONS[self.video_aspect_ratio]["size"]
```

**Global State**:
- `current_config: Optional[GenerationConfig]` - Module-level singleton
- `get_current_config()` / `set_current_config()` - Accessors used by agent

---

### 3. `content_generator_agent.py` - LangChain Agent

**Purpose**: Orchestrates tool calls using GPT-5 as the reasoning engine.

**Agent Creation**:
```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5",          # LangChain model string format
    tools=[                         # List of @tool decorated functions
        generate_image,
        generate_video,
        generate_caption,
        check_policy_compliance,
        check_design_compliance
    ],
    system_prompt=get_system_prompt()  # Dynamic prompt with config values
)
```

**System Prompt Injection**:
The `get_system_prompt()` function reads `GenerationConfig` and injects:
- Current video/image settings
- Whether to auto-run compliance checks
- Instructions for tool usage patterns

**Conversation Memory**:
```python
class ContentGeneratorAgent:
    def __init__(self):
        self.chat_history = []  # List[dict] with role/content
    
    def chat(self, user_input: str) -> str:
        self.chat_history.append({"role": "user", "content": user_input})
        response = self.agent.invoke({"messages": self.chat_history})
        # Extract AI response from messages, append to history
```

---

### 4. `tools/image_generator.py` - DALL-E 3 Integration

**Purpose**: Generate images and save locally.

**API Call**:
```python
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size=size,          # "1024x1024" | "1792x1024" | "1024x1792"
    quality=quality,    # "standard" | "hd"
    n=1
)

image_url = response.data[0].url
revised_prompt = response.data[0].revised_prompt
```

**Local Download**:
```python
def download_image(url: str, filename: str) -> str:
    response = requests.get(url, timeout=60)
    filepath = Path("generated_content/images") / filename
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return str(filepath.absolute())
```

**Tool Decorator**:
```python
@tool
def generate_image(prompt: str, size: str = "1024x1024", quality: str = "hd") -> str:
    """Docstring becomes tool description for LLM"""
```

---

### 5. `tools/video_generator.py` - Sora-2 Integration

**Purpose**: Generate videos with aspect ratio → resolution mapping.

**Aspect Ratio Mapping**:
```python
ASPECT_RATIO_MAP = {
    "16:9": {"size": "1920x1080", "platforms": ["YouTube", "LinkedIn"]},
    "9:16": {"size": "1080x1920", "platforms": ["TikTok", "Reels"]},
    "1:1":  {"size": "1080x1080", "platforms": ["Instagram Feed"]},
    "4:5":  {"size": "1080x1350", "platforms": ["Instagram optimal"]},
    "21:9": {"size": "2560x1080", "platforms": ["Cinematic"]},
}
```

**API Call**:
```python
response = client.videos.create(
    model="sora-2",
    prompt=prompt,
    size=ASPECT_RATIO_MAP[aspect_ratio]["size"],  # e.g., "1920x1080"
    seconds=seconds  # 5-60
)
video_url = response.data[0].url
```

**Local Download**:
```python
video_content = client.videos.download_content(response.data[0].id)
with open(local_path, 'wb') as f:
    f.write(video_content)
```

---

### 6. `tools/caption_generator.py` - Caption + Hashtags

**Purpose**: Platform-optimized captions using GPT-5 chat completion.

**Platform Guidelines**:
```python
platform_guidelines = {
    "instagram": {"max_length": 2200, "hashtag_count": "20-30"},
    "linkedin":  {"max_length": 3000, "hashtag_count": "3-5"},
    "twitter":   {"max_length": 280,  "hashtag_count": "1-3"},
    # ...
}
```

**API Call**:
```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": system_prompt},  # Platform rules
        {"role": "user", "content": user_prompt}       # Content description
    ],
    temperature=0.8,
    max_tokens=1000
)
```

---

### 7. `tools/policy_checker.py` - Policy Compliance Agent

**Purpose**: Validate content against `guidelines/policy_guidelines.md`.

**Guideline Loading**:
```python
def load_policy_guidelines() -> str:
    path = Path(__file__).parent.parent / "guidelines" / "policy_guidelines.md"
    with open(path, 'r') as f:
        return f.read()
```

**Compliance Check**:
```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": f"""
            You are a compliance reviewer.
            GUIDELINES: {policy_guidelines}
            Output format: PASS/WARNING/FAIL with category breakdown
        """},
        {"role": "user", "content": f"Review: {content_description}"}
    ],
    temperature=0.3  # Lower for consistency
)
```

---

### 8. `tools/design_checker.py` - Design Compliance Agent

**Purpose**: Validate visual content against `guidelines/design_guidelines.md`.

**Same pattern as policy_checker**, but:
- Loads `design_guidelines.md`
- Focuses on visual aspects: color, composition, resolution, accessibility
- Flags items requiring manual visual review

---

## Data Flow

### Content Generation Flow:
```
1. User: "Create an Instagram post for our product launch"
2. GPT-5 (agent): Analyzes request, decides to call tools
3. Agent calls: generate_image(prompt="...", size="1024x1024")
4. DALL-E 3: Returns image URL
5. Tool: Downloads image to generated_content/images/
6. Agent calls: generate_caption(content_description="...", platform="instagram")
7. GPT-5: Returns formatted caption with hashtags
8. If auto_compliance_check=True:
   - Agent calls: check_policy_compliance(...)
   - Agent calls: check_design_compliance(...)
9. Agent: Compiles all results into response
```

### Configuration Flow:
```
1. main.py calls get_config_from_user()
2. User inputs values (or accepts defaults)
3. config.py creates GenerationConfig dataclass
4. set_current_config(config) stores globally
5. Agent's get_system_prompt() reads config for prompt injection
6. Tools access config via get_current_config()
```

---

## File Output Structure

```
generated_content/
├── images/
│   ├── image_20241207_153045.png
│   └── image_20241207_154512.png
└── videos/
    └── video_20241207_160023.mp4
```

Filenames use timestamp format: `{type}_{YYYYMMDD}_{HHMMSS}.{ext}`

---

## Environment Variables

```
OPENAI_API_KEY=sk-...  # Required for all API calls
```

Loaded via `python-dotenv` in `content_generator_agent.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Reads .env file
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `openai>=1.40.0` | DALL-E 3, Sora-2, GPT-5 API client |
| `langchain>=0.3.0` | Agent framework with `create_agent()` |
| `langchain-openai` | OpenAI integration for LangChain |
| `langchain-core` | Core abstractions, `@tool` decorator |
| `python-dotenv` | Load `.env` file |
| `requests` | Download images from URLs |

---

## Error Handling

- **Lazy Client Initialization**: `get_client()` functions create OpenAI client on first tool call, not at import time (avoids errors when API key not set during import)
- **Validation**: Tools validate parameters against allowed values, falling back to defaults
- **Exception Wrapping**: All tools return error messages as strings (`❌ Error: {str(e)}`) instead of raising

---

## Extension Points

1. **Add New Tools**: Create function with `@tool` decorator in `tools/`, add to `tools/__init__.py`, register in `create_content_agent()`

2. **Custom Guidelines**: Replace `guidelines/*.md` files with your own policy/design rules

3. **Programmatic Use**: 
```python
from content_generator_agent import ContentGeneratorAgent
from config import set_current_config, GenerationConfig

config = GenerationConfig(video_duration=15, auto_compliance_check=False)
set_current_config(config)
agent = ContentGeneratorAgent()
response = agent.chat("Create a LinkedIn post about AI")
```
