"""
Design Compliance Checker Agent.
Reviews generated visual content against the simplified design guidelines.
"""

import os
from pathlib import Path
from langchain.tools import tool
from openai import OpenAI


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client():
    """Get OpenAI client - created on first call to avoid import errors."""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_design_guidelines() -> str:
    """Load design guidelines from file."""
    guidelines_path = Path(__file__).parent.parent / "guidelines" / "design_guidelines.md"
    
    if guidelines_path.exists():
        with open(guidelines_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fallback if file doesn't exist
    return """## Colors
- Professional, brand-appropriate colors
- High contrast for text
- No neon/oversaturated

## Composition
- Subject centered or rule-of-thirds
- Clean backgrounds
- Proper lighting

## Quality
- Minimum 1080p
- Sharp focus
- No watermarks

## Accessibility
- Good color contrast
- No flashing effects"""


# =============================================================================
# MAIN TOOL
# =============================================================================

@tool
def check_design_compliance(
    content_description: str,
    content_type: str = "image",
    resolution: str = ""
) -> str:
    """
    Check if generated visual content complies with design guidelines.
    
    Args:
        content_description: Description of the image/video visual elements.
        content_type: Either "image" or "video".
        resolution: Resolution if known (e.g., "1920x1080").
    
    Returns:
        Design compliance report with pass/fail status and recommendations.
    """
    try:
        design_guidelines = load_design_guidelines()
        client = get_client()
        
        # System prompt tells GPT how to evaluate
        system_prompt = f"""You are a design compliance reviewer for visual content.
Evaluate the content against these guidelines:

{design_guidelines}

EVALUATION CRITERIA:
1. COLORS - Professional colors, high contrast, no neon
2. COMPOSITION - Good framing, clean background, proper lighting
3. QUALITY - High resolution, sharp focus, no artifacts
4. ACCESSIBILITY - Good contrast, no strobing

NOTE: You cannot see the actual {content_type}, so evaluate based on the description.
Flag items that need manual visual review.

OUTPUT FORMAT (use exactly this format):
═══════════════════════════════════════
   DESIGN COMPLIANCE REPORT
═══════════════════════════════════════

STATUS: [✅ PASS / ⚠️ WARNING / ❌ FAIL]
SCORE: [X/10]
TYPE: [{content_type.upper()}]

CHECKS:
• Colors: [✅/⚠️/❌] [brief note]
• Composition: [✅/⚠️/❌] [brief note]
• Quality: [✅/⚠️/❌] [brief note]
• Accessibility: [✅/⚠️/❌] [brief note]

ISSUES: [List any problems, or "None identified"]

NEEDS MANUAL REVIEW: [List items requiring visual check]

RECOMMENDATIONS: [List suggestions if needed]
═══════════════════════════════════════
"""

        user_prompt = f"""Review this {content_type}:

DESCRIPTION: {content_description}
RESOLUTION: {resolution if resolution else "Not specified"}

Provide your design compliance assessment."""

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Design compliance check failed: {str(e)}"
