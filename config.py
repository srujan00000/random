"""
Configuration module for the Content Generation Agent.
Handles runtime configuration for video generation and caption settings.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationConfig:
    """Configuration settings for content generation."""
    
    # Video settings
    video_duration: int = 10  # Duration in seconds (5-60)
    video_resolution: str = "1080p"  # Options: 720p, 1080p, 4k
    video_aspect_ratio: str = "16:9"  # Options: 16:9, 9:16, 1:1
    
    # Caption settings
    enable_captions: bool = True
    caption_style: str = "professional"  # Options: professional, casual, creative
    
    # Image settings
    image_size: str = "1024x1024"  # Options: 1024x1024, 1792x1024, 1024x1792
    image_quality: str = "hd"  # Options: standard, hd
    
    def __str__(self) -> str:
        return f"""
┌─────────────────────────────────────┐
│     Current Configuration           │
├─────────────────────────────────────┤
│ Video Duration: {self.video_duration}s
│ Video Resolution: {self.video_resolution}
│ Aspect Ratio: {self.video_aspect_ratio}
│ Captions Enabled: {self.enable_captions}
│ Caption Style: {self.caption_style}
│ Image Size: {self.image_size}
│ Image Quality: {self.image_quality}
└─────────────────────────────────────┘
"""


def get_config_from_user() -> GenerationConfig:
    """Interactive prompt to get configuration from user."""
    
    print("\n🔧 Configuration Setup")
    print("=" * 40)
    
    config = GenerationConfig()
    
    # Video Duration
    print("\n📹 Video Settings:")
    duration_input = input(f"  Video duration in seconds (5-60) [default: {config.video_duration}]: ").strip()
    if duration_input:
        try:
            duration = int(duration_input)
            if 5 <= duration <= 60:
                config.video_duration = duration
            else:
                print("  ⚠️  Invalid range. Using default.")
        except ValueError:
            print("  ⚠️  Invalid input. Using default.")
    
    # Video Resolution
    resolution_input = input(f"  Video resolution (720p/1080p/4k) [default: {config.video_resolution}]: ").strip().lower()
    if resolution_input in ["720p", "1080p", "4k"]:
        config.video_resolution = resolution_input
    elif resolution_input:
        print("  ⚠️  Invalid option. Using default.")
    
    # Aspect Ratio
    aspect_input = input(f"  Aspect ratio (16:9/9:16/1:1) [default: {config.video_aspect_ratio}]: ").strip()
    if aspect_input in ["16:9", "9:16", "1:1"]:
        config.video_aspect_ratio = aspect_input
    elif aspect_input:
        print("  ⚠️  Invalid option. Using default.")
    
    # Caption Toggle
    print("\n📝 Caption Settings:")
    caption_input = input(f"  Enable captions? (yes/no) [default: {'yes' if config.enable_captions else 'no'}]: ").strip().lower()
    if caption_input in ["yes", "y", "true", "1"]:
        config.enable_captions = True
    elif caption_input in ["no", "n", "false", "0"]:
        config.enable_captions = False
    
    # Caption Style (only if captions are enabled)
    if config.enable_captions:
        style_input = input(f"  Caption style (professional/casual/creative) [default: {config.caption_style}]: ").strip().lower()
        if style_input in ["professional", "casual", "creative"]:
            config.caption_style = style_input
        elif style_input:
            print("  ⚠️  Invalid option. Using default.")
    
    # Image Settings
    print("\n🖼️  Image Settings:")
    size_input = input(f"  Image size (1024x1024/1792x1024/1024x1792) [default: {config.image_size}]: ").strip()
    if size_input in ["1024x1024", "1792x1024", "1024x1792"]:
        config.image_size = size_input
    elif size_input:
        print("  ⚠️  Invalid option. Using default.")
    
    quality_input = input(f"  Image quality (standard/hd) [default: {config.image_quality}]: ").strip().lower()
    if quality_input in ["standard", "hd"]:
        config.image_quality = quality_input
    elif quality_input:
        print("  ⚠️  Invalid option. Using default.")
    
    print("\n✅ Configuration saved!")
    print(config)
    
    return config


# Global config instance - will be set by main.py
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
