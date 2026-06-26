"""Post reels/videos to Instagram and Facebook via Graph API."""
import os
import time
import requests

GRAPH = "https://graph.facebook.com/v21.0"


def _token():
    return os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")


def _page_token(user_token, page_id):
    resp = requests.get(
        f"{GRAPH}/{page_id}",
        params={"fields": "access_token", "access_token": user_token},
        timeout=30,
    ).json()
    if "access_token" not in resp:
        raise RuntimeError(f"Could not get Page token: {resp}")
    return resp["access_token"]


def post_reel_to_instagram(video_url, caption, cover_url=None):
    """Post a video URL as an Instagram Reel. Returns media ID."""
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
    token      = _token()

    params = {
        "media_type":    "REELS",
        "video_url":     video_url,
        "caption":       caption,
        "share_to_feed": "true",
        "access_token":  token,
    }
    if cover_url:
        params["cover_url"] = cover_url

    print("Creating Instagram Reel container...")
    resp = requests.post(f"{GRAPH}/{account_id}/media", params=params, timeout=60).json()
    if "id" not in resp:
        raise RuntimeError(f"IG container error: {resp}")

    container_id = resp["id"]
    print("Waiting for Instagram to process...", end="", flush=True)
    for _ in range(20):
        time.sleep(15)
        st = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        ).json().get("status_code", "")
        print(".", end="", flush=True)
        if st == "FINISHED":
            break
        if st == "ERROR":
            raise RuntimeError("Instagram container processing failed")
    print()

    pub = requests.post(
        f"{GRAPH}/{account_id}/media_publish",
        params={"creation_id": container_id, "access_token": token},
        timeout=60,
    ).json()
    if "id" not in pub:
        raise RuntimeError(f"IG publish error: {pub}")

    media_id = pub["id"]
    print(f"Instagram Reel live: https://www.instagram.com/reel/{media_id}/")
    return media_id


def post_comment_to_instagram(media_id, text):
    """Post a comment on an IG media object (used for hashtags / reveal)."""
    token = _token()
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
    resp = requests.post(
        f"{GRAPH}/{media_id}/comments",
        params={"message": text, "access_token": token},
        timeout=30,
    ).json()
    if "id" not in resp:
        raise RuntimeError(f"IG comment error: {resp}")
    return resp["id"]


def post_video_to_facebook(video_url, caption, title=None):
    """Post a video URL to the Facebook Page. Returns video ID."""
    page_id    = os.environ.get("FACEBOOK_PAGE_ID", "")
    user_token = _token()
    page_token = _page_token(user_token, page_id)

    params = {
        "file_url":     video_url,
        "description":  caption,
        "access_token": page_token,
    }
    if title:
        params["title"] = title[:100]

    print("Posting video to Facebook...")
    resp = requests.post(f"{GRAPH}/{page_id}/videos", params=params, timeout=60).json()
    if "id" not in resp:
        raise RuntimeError(f"FB video error: {resp}")

    video_id = resp["id"]
    print("Waiting for Facebook to process...", end="", flush=True)
    for _ in range(30):
        time.sleep(6)
        st = requests.get(
            f"{GRAPH}/{video_id}",
            params={"fields": "status", "access_token": page_token},
            timeout=30,
        ).json().get("status", {}).get("video_status", "")
        print(".", end="", flush=True)
        if st == "ready":
            break
        if st == "error":
            raise RuntimeError(f"FB video processing failed")
    print()
    print(f"Facebook video posted: {video_id}")
    return video_id
