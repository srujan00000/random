import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_URN = os.getenv("LINKEDIN_URN")  # e.g., "urn:li:person:abc123"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def post_linkedin_image(caption_prompt, image_path):
    """Generate caption, upload image, and post to LinkedIn feed."""

    def generate_caption(prompt):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Write a professional LinkedIn post caption."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def register_upload():
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "registerUploadRequest": {
                "owner": LINKEDIN_URN,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        response = requests.post(url, json=payload, headers=headers).json()
        upload_url = response["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = response["value"]["asset"]
        return upload_url, asset_urn

    def upload_image(upload_url, image_path):
        with open(image_path, "rb") as img:
            response = requests.put(upload_url, data=img, headers={
                "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                "Content-Type": "image/jpeg"
            })
        return response.status_code == 201 or response.status_code == 200

    def create_post(text, asset_urn):
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "author": LINKEDIN_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": text},
                        "media": asset_urn,
                        "title": {"text": "Post"}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        return requests.post(url, json=payload, headers=headers).json()

    caption = generate_caption(caption_prompt)
    upload_url, asset_urn = register_upload()
    if not upload_image(upload_url, image_path):
        raise RuntimeError("Image upload failed")
    result = create_post(caption, asset_urn)
    print("Image Post Result:", result)
    return result

def post_linkedin_video(caption_prompt, video_path, title="Video"):
    """Generate caption, upload video, and post to LinkedIn feed."""

    def generate_caption(prompt):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Write a professional LinkedIn post caption."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    def register_upload():
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "registerUploadRequest": {
                "owner": LINKEDIN_URN,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        response = requests.post(url, json=payload, headers=headers).json()
        upload_url = response["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = response["value"]["asset"]
        return upload_url, asset_urn

    def upload_video(upload_url, video_path):
        try:
            from mimetypes import guess_type
            content_type, _ = guess_type(video_path)
        except Exception:
            content_type = None
        if not content_type:
            content_type = "video/mp4"
        with open(video_path, "rb") as vf:
            response = requests.put(
                upload_url,
                data=vf,
                headers={
                    "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
                    "Content-Type": content_type
                }
            )
        return response.status_code == 201 or response.status_code == 200

    def create_post(text, asset_urn, title):
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "author": LINKEDIN_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "VIDEO",
                    "media": [{
                        "status": "READY",
                        "description": {"text": text},
                        "media": asset_urn,
                        "title": {"text": title}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        return requests.post(url, json=payload, headers=headers).json()

    caption = generate_caption(caption_prompt)
    upload_url, asset_urn = register_upload()
    if not upload_video(upload_url, video_path):
        raise RuntimeError("Video upload failed")
    result = create_post(caption, asset_urn, title)
    print("Video Post Result:", result)
    return result

if __name__ == "__main__":
    # Uncomment and use as needed:
    # post_linkedin_image("Announcing our new AI automation tool.", "OIP.jpg")
    post_linkedin_video("Cute cat video doing trick.", "Cute_cat.mp4", title="Cute cat")
