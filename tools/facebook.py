import os
import mimetypes
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GRAPH_API_BASE = "https://graph.facebook.com/v24.0"

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_caption(prompt: str) -> str:
    """
    Uses OpenAI to generate a short caption with hashtags.
    """
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not set – cannot generate caption.")

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You write short, engaging Instagram and Facebook captions."},
            {
                "role": "user",
                "content": f"Write a short caption (max 2 lines) with 5 relevant hashtags for: {prompt}"
            }
        ],
        max_completion_tokens=120,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def get_page_access_token() -> str:
    """
    Returns a Page access token for FB_PAGE_ID if META_ACCESS_TOKEN is a user token with permissions.
    Falls back to META_ACCESS_TOKEN if exchange fails.
    """
    if not META_ACCESS_TOKEN:
        raise RuntimeError("META_ACCESS_TOKEN is not set.")
    if not FB_PAGE_ID:
        raise RuntimeError("FB_PAGE_ID is not set.")

    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}"
    params = {"fields": "access_token", "access_token": META_ACCESS_TOKEN}
    try:
        r = requests.get(url, params=params, timeout=30)
        j = r.json()
        if r.ok and isinstance(j, dict) and j.get("access_token"):
            return j["access_token"]
        else:
            print("[FB] Could not retrieve Page access token; using provided META_ACCESS_TOKEN. Response:", j if isinstance(j, dict) else r.text[:200])
            return META_ACCESS_TOKEN
    except Exception as e:
        print("[FB] Page token fetch failed:", repr(e))
        return META_ACCESS_TOKEN


def post_facebook_image(prompt: str, image_path: str, published: bool = True) -> dict:
    """
    Generate a caption and post a local image file to the Facebook Page as a photo.
    - image_path: local path to an image (jpg, png, gif, etc.)
    - published: whether to publish immediately
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    caption = generate_caption(prompt)
    page_token = get_page_access_token()
    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/photos"

    # Guess MIME type
    mime, _ = mimetypes.guess_type(image_path)
    if not mime:
        # reasonable default
        mime = "image/jpeg"

    params = {
        "access_token": page_token,
        "caption": caption,
        "published": "true" if published else "false",
    }

    print(f"[FB] Posting image to: {url}")
    with open(image_path, "rb") as f:
        files = {"source": (os.path.basename(image_path), f, mime)}
        r = requests.post(url, data=params, files=files, timeout=120)

    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if r.status_code >= 400:
        print("[FB] Image Error:", data)
        r.raise_for_status()

    print("[FB] Image Response:", data)
    return data


def post_facebook_video(prompt: str, video_path: str, title: str | None = None, published: bool = True) -> dict:
    """
    Generate a caption and post a local video file to the Facebook Page.
    - video_path: local path to the video file (e.g., .mp4)
    - title: optional video title
    - published: whether to publish immediately
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    description = generate_caption(prompt)
    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/videos"
    page_token = get_page_access_token()
    params = {
        "access_token": page_token,
        "description": description,
        "published": "true" if published else "false",
    }
    if title:
        params["title"] = title

    files = {
        "source": (os.path.basename(video_path), open(video_path, "rb"), "video/mp4")
    }

    print(f"[FB] Posting video to: {url}")
    r = requests.post(url, data=params, files=files)

    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}

    if r.status_code >= 400:
        print("[FB] Video Error:", data)
        r.raise_for_status()

    print("[FB] Video Response:", data)
    return data


if __name__ == "__main__":
    # Example: Post an image to Facebook (NOT Instagram)
    # Ensure OIP.jpg exists in the current directory and .env has META_ACCESS_TOKEN and FB_PAGE_ID set.
    post_facebook_image("Announcing our new AI automation tool.", "OIP.jpg")

    # Example: Post a video to Facebook (uncomment if needed)
    # post_facebook_video("Announcing our new AI automation tool.", "Cute_cat.mp4", title="Cute cat")
