"""
Configuration module for the Content Generation Agent.
Handles runtime configuration for content generation, publishing, and compliance.
"""

from dataclasses import dataclass, field
from typing import Optional, List


# =============================================================================
# CONSTANTS
# =============================================================================

# Aspect ratio to resolution mapping
ASPECT_RATIO_OPTIONS = {
    "16:9": {"size": "1920x1080", "desc": "Landscape - YouTube, LinkedIn, Twitter"},
    "9:16": {"size": "1080x1920", "desc": "Portrait - TikTok, Reels, Shorts"},
    "1:1": {"size": "1080x1080", "desc": "Square - Instagram Feed, Facebook"},
    "4:5": {"size": "1080x1350", "desc": "Portrait - Instagram Feed optimal"}
}

# Available platforms for publishing
AVAILABLE_PLATFORMS = ["linkedin", "instagram", "facebook"]


# =============================================================================
# CONFIGURATION DATACLASS
# =============================================================================

@dataclass
class GenerationConfig:
    """Configuration settings for content generation and publishing."""
    
    # Target platforms for publishing (can be multiple)
    target_platforms: List[str] = field(default_factory=lambda: ["linkedin"])
    
    # Video settings
    video_duration: int = 10  # Duration in seconds (5-60)
    video_aspect_ratio: str = "16:9"  # Auto-selected based on platform if not specified
    
    # Caption settings
    enable_captions: bool = True
    caption_style: str = "professional"  # professional, casual, creative
    
    # Image settings
    image_size: str = "1024x1024"  # 1024x1024, 1792x1024, 1024x1792
    image_quality: str = "hd"  # standard, hd
    
    # Compliance settings
    auto_compliance_check: bool = True
    
    # Publishing settings
    auto_publish: bool = False  # If True, publish immediately after generation
    
    @property
    def video_resolution(self) -> str:
        """Get video resolution based on aspect ratio."""
        return ASPECT_RATIO_OPTIONS.get(self.video_aspect_ratio, ASPECT_RATIO_OPTIONS["16:9"])["size"]
    
    @property
    def platforms_display(self) -> str:
        """Get comma-separated list of platforms for display."""
        return ", ".join([p.capitalize() for p in self.target_platforms])
    
    def __str__(self) -> str:
        resolution = self.video_resolution
        return f"""
┌────────────────────────────────────────────────────────────┐
│              Current Configuration                          │
├────────────────────────────────────────────────────────────┤
│ 📱 TARGET PLATFORMS: {self.platforms_display:<35} │
│                                                             │
│ 📹 VIDEO: {self.video_duration}s, {self.video_aspect_ratio} ({resolution})
│ 🖼️  IMAGE: {self.image_size}, {self.image_quality} quality
│ 📝 CAPTIONS: {self.enable_captions}, style={self.caption_style}
│ ✅ AUTO-COMPLIANCE: {self.auto_compliance_check}
│ 🚀 AUTO-PUBLISH: {self.auto_publish}
└────────────────────────────────────────────────────────────┘
"""


# =============================================================================
# INTERACTIVE CONFIGURATION
# =============================================================================

def get_config_from_user() -> GenerationConfig:
    """Interactive prompt to get configuration from user."""
    
    print("\n🔧 Configuration Setup")
    print("=" * 55)
    
    config = GenerationConfig()
    
    # =========================================================================
    # PLATFORM SELECTION (Most important - asked first)
    # =========================================================================
    print("\n📱 Target Platforms:")
    print("  Available: linkedin, instagram, facebook")
    print("  (You can select multiple, comma-separated)")
    
    platforms_input = input("  Platforms [default: linkedin]: ").strip().lower()
    if platforms_input:
        # Parse comma-separated platforms
        selected = [p.strip() for p in platforms_input.split(",")]
        # Filter to only valid platforms
        valid_selected = [p for p in selected if p in AVAILABLE_PLATFORMS]
        if valid_selected:
            config.target_platforms = valid_selected
        else:
            print("  ⚠️  No valid platforms. Using default (linkedin).")
    
    # =========================================================================
    # VIDEO SETTINGS
    # =========================================================================
    print("\n📹 Video Settings:")
    
    # Duration
    duration_input = input(f"  Duration in seconds (5-60) [default: {config.video_duration}]: ").strip()
    if duration_input:
        try:
            duration = int(duration_input)
            if 5 <= duration <= 60:
                config.video_duration = duration
            else:
                print("  ⚠️  Invalid range. Using default.")
        except ValueError:
            print("  ⚠️  Invalid input. Using default.")
    
    # Aspect Ratio
    print("\n  Aspect ratios:")
    for ratio, info in ASPECT_RATIO_OPTIONS.items():
        print(f"    • {ratio} ({info['size']}) - {info['desc']}")
    
    aspect_input = input(f"\n  Aspect ratio [default: {config.video_aspect_ratio}]: ").strip()
    if aspect_input in ASPECT_RATIO_OPTIONS:
        config.video_aspect_ratio = aspect_input
    elif aspect_input:
        print("  ⚠️  Invalid option. Using default.")
    
    # =========================================================================
    # IMAGE SETTINGS
    # =========================================================================
    print("\n🖼️  Image Settings:")
    print("  Sizes: 1024x1024 (square), 1792x1024 (landscape), 1024x1792 (portrait)")
    
    size_input = input(f"  Image size [default: {config.image_size}]: ").strip()
    if size_input in ["1024x1024", "1792x1024", "1024x1792"]:
        config.image_size = size_input
    elif size_input:
        print("  ⚠️  Invalid option. Using default.")
    
    # =========================================================================
    # CAPTION SETTINGS
    # =========================================================================
    print("\n📝 Caption Settings:")
    caption_input = input(f"  Enable captions? (yes/no) [default: yes]: ").strip().lower()
    if caption_input in ["no", "n", "false", "0"]:
        config.enable_captions = False
    
    if config.enable_captions:
        style_input = input(f"  Style (professional/casual/creative) [default: {config.caption_style}]: ").strip().lower()
        if style_input in ["professional", "casual", "creative"]:
            config.caption_style = style_input
    
    # =========================================================================
    # COMPLIANCE & PUBLISHING
    # =========================================================================
    print("\n⚙️  Workflow Settings:")
    
    compliance_input = input("  Auto-run compliance checks? (yes/no) [default: yes]: ").strip().lower()
    if compliance_input in ["no", "n", "false", "0"]:
        config.auto_compliance_check = False
    
    publish_input = input("  Auto-publish after generation? (yes/no) [default: no]: ").strip().lower()
    if publish_input in ["yes", "y", "true", "1"]:
        config.auto_publish = True
    
    # Print final config
    print("\n✅ Configuration saved!")
    print(config)
    
    return config


# =============================================================================
# GLOBAL CONFIG STATE
# =============================================================================

# Global config instance - set by main.py
current_config: Optional[GenerationConfig] = None


def get_current_config() -> GenerationConfig:
    """Get the current configuration, creating default if none exists."""
    global current_config
    if current_config is None:
        current_config = GenerationConfig()
    return current_config


def set_current_config(config: GenerationConfig) -> None:
    """Set the global configuration."""
    global current_config
    current_config = config
