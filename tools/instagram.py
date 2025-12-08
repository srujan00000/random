import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
GRAPH_API_BASE = "https://graph.facebook.com/v24.0"

def generate_caption_with_llm(prompt: str) -> str:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not set – cannot generate caption.")
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You write short, engaging Instagram and Facebook captions."},
            {"role": "user", "content": f"Write a short caption (max 2 lines) with 5 relevant hashtags for: {prompt}"}
        ],
        max_completion_tokens=120,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

def get_page_access_token() -> str:
    token = META_ACCESS_TOKEN
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN is not set.")
    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}"
    params = {"fields": "access_token", "access_token": token}
    try:
        r = requests.get(url, params=params, timeout=30)
        j = r.json()
        if r.ok and isinstance(j, dict) and j.get("access_token"):
            return j["access_token"]
        else:
            print("[FB] Could not retrieve Page access token; using provided META_ACCESS_TOKEN.")
            return token
    except Exception as e:
        print("[FB] Page token fetch failed:", repr(e))
        return token

def upload_image_via_facebook_page(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    url = f"{GRAPH_API_BASE}/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as imgfile:
        files = {"source": imgfile}
        page_token = get_page_access_token()
        params = {"access_token": page_token, "published": "false"}
        r = requests.post(url, data=params, files=files, timeout=60)
    data = r.json()
    if r.status_code >= 400:
        raise RuntimeError(f"[FB Upload] Error: {data}")
    photo_id = data.get("id")
    if not photo_id:
        raise RuntimeError("Facebook upload did not return a photo id.")

    # Get the direct CDN URL
    info_url = f"{GRAPH_API_BASE}/{photo_id}"
    info_params = {"fields": "images,link", "access_token": page_token}
    info_res = requests.get(info_url, params=info_params, timeout=30)
    info = info_res.json()
    if info_res.status_code >= 400:
        raise RuntimeError(f"[FB Upload] Query Error: {info}")
    images = info.get("images", [])
    if images:
        src = images[0].get("source")
        if src and src.startswith("http"):
            print("[IG] Uploaded to Facebook CDN:", src)
            return src
    possible = info.get("link")
    if possible and isinstance(possible, str) and possible.startswith("http"):
        print("[IG] Uploaded using Facebook link:", possible)
        return possible
    raise RuntimeError("Failed to obtain a public URL from Facebook upload.")

def create_ig_media_container(image_url: str, caption: str) -> str:
    url = f"{GRAPH_API_BASE}/{IG_USER_ID}/media"
    payload = {"image_url": image_url, "caption": caption, "access_token": META_ACCESS_TOKEN}
    r = requests.post(url, data=payload)
    data = r.json()
    if r.status_code >= 400:
        raise RuntimeError(f"[IG] Container Error: {data}")
    return data["id"]

def publish_ig_container(container_id: str) -> str:
    url = f"{GRAPH_API_BASE}/{IG_USER_ID}/media_publish"
    payload = {"creation_id": container_id, "access_token": META_ACCESS_TOKEN}
    r = requests.post(url, data=payload)
    data = r.json()
    if r.status_code >= 400:
        raise RuntimeError(f"[IG] Publish Error: {data}")
    return data.get("id", "")

def post_to_instagram_local(image_path: str, caption: str) -> None:
    public_url = upload_image_via_facebook_page(image_path)
    print("[IG] Creating media container…")
    container_id = create_ig_media_container(public_url, caption)
    print(f"[IG] Container created: {container_id}, publishing…")
    media_id = publish_ig_container(container_id)
    print(f"[IG] Published on Instagram. Media ID: {media_id}")

if __name__ == "__main__":
    ig_caption = generate_caption_with_llm("Announcing our new AI automation tool.")
    post_to_instagram_local("OIP.jpg", ig_caption)
