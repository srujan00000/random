"""
Policy Compliance Checker Agent.
Reviews generated content against the simplified policy guidelines.
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


def load_policy_guidelines() -> str:
    """Load policy guidelines from file."""
    guidelines_path = Path(__file__).parent.parent / "guidelines" / "policy_guidelines.md"
    
    if guidelines_path.exists():
        with open(guidelines_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Fallback if file doesn't exist
    return """## Prohibited Content
- Violence, weapons, harmful activities
- Discrimination
- Misleading claims
- Copyrighted materials
- Political content
- Explicit content

## Brand Voice
- Professional tone
- Inclusive language
- No exaggerated claims

## Legal
- Label sponsored content
- Use licensed content only"""


# =============================================================================
# MAIN TOOL
# =============================================================================

@tool
def check_policy_compliance(
    content_description: str,
    caption: str = "",
    platform: str = "general"
) -> str:
    """
    Check if generated content complies with policy guidelines.
    
    Args:
        content_description: Description of the image/video content.
        caption: The caption/text that accompanies the content (if any).
        platform: Target platform (linkedin, instagram, facebook).
    
    Returns:
        Compliance report with pass/fail status and recommendations.
    """
    try:
        policy_guidelines = load_policy_guidelines()
        client = get_client()
        
        # System prompt tells GPT how to evaluate
        system_prompt = f"""You are a content policy compliance reviewer.
Evaluate the content against these guidelines:

{policy_guidelines}

EVALUATION CRITERIA:
1. PROHIBITED CONTENT - Check for violence, discrimination, misleading claims, copyright issues
2. BRAND VOICE - Professional, inclusive, no exaggerations
3. PLATFORM FIT - Appropriate tone for {platform} (LinkedIn=professional, Instagram=casual OK, Facebook=conversational)
4. LEGAL - Proper disclosures if needed

OUTPUT FORMAT (use exactly this format):
═══════════════════════════════════════
   POLICY COMPLIANCE REPORT
═══════════════════════════════════════

STATUS: [✅ PASS / ⚠️ WARNING / ❌ FAIL]
SCORE: [X/10]

CHECKS:
• Prohibited Content: [✅/❌] [brief note]
• Brand Voice: [✅/❌] [brief note]  
• Platform Fit: [✅/❌] [brief note]
• Legal Compliance: [✅/❌] [brief note]

ISSUES: [List any problems, or "None"]

RECOMMENDATIONS: [List fixes if needed, or "Content is compliant"]
═══════════════════════════════════════
"""

        user_prompt = f"""Review this content:

PLATFORM: {platform}
CONTENT: {content_description}
CAPTION: {caption if caption else "None provided"}

Provide your compliance assessment."""

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
        return f"❌ Policy compliance check failed: {str(e)}"
