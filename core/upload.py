import os
import requests
from telegram import Bot

# Telegram integration
TELEGRAM_BOT = Bot(token=os.getenv("BOT_TOKEN"))
AFFILIATE_ID_AE = os.getenv("AFFILIATE_ID_AE")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
TELEGRAM_CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME")


def _append_affiliate(url: str) -> str:
    sep = '&' if '?' in url else '?'
    return f"{url}{sep}aff_id={AFFILIATE_ID_AE}"


def upload_drafts(video_bytes: bytes, platforms: list[str]) -> list[str]:
    links = []
    for p in platforms:
        if p == 'vk':
            links.append(_upload_vk(video_bytes))
        elif p == 'tiktok':
            links.append(_upload_tiktok(video_bytes))
        elif p == 'instagram':
            links.append(_upload_instagram(video_bytes))
        elif p == 'telegram':
            links.append(_upload_telegram(video_bytes))
    return links


def _upload_vk(video_bytes: bytes) -> str:
    vk_token = os.getenv("VK_TOKEN")
    save_resp = requests.get(
        "https://api.vk.com/method/video.save",
        params={"access_token": vk_token, "v": "5.131"}
    ).json()
    upload_url = save_resp['response']['upload_url']
    files = {"video_file": ("video.mp4", video_bytes, "video/mp4")}
    upload_resp = requests.post(upload_url, files=files)
    upload_resp.raise_for_status()
    info = upload_resp.json()
    owner, vid = info['owner_id'], info['video_id']
    return f"https://vk.com/video{owner}_{vid}"


def _upload_tiktok(video_bytes: bytes) -> str:
    ttoken = os.getenv("TIKTOK_TOKEN")
    url = "https://open.tiktokapis.com/v1/video/upload"
    headers = {"Authorization": f"Bearer {ttoken}"}
    files = {"video": ("video.mp4", video_bytes, "video/mp4")}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json().get('data', {}).get('share_url', '')


def _upload_instagram(video_bytes: bytes) -> str:
    ig_token = os.getenv("IG_TOKEN")
    ig_user = os.getenv("IG_USER_ID")
    media_resp = requests.post(
        f"https://graph.facebook.com/v15.0/{ig_user}/media",
        params={"access_token": ig_token},
        files={"video_file": ("video.mp4", video_bytes, "video/mp4")}
    )
    media_resp.raise_for_status()
    creation_id = media_resp.json().get('id')
    publish_resp = requests.post(
        f"https://graph.facebook.com/v15.0/{ig_user}/media_publish",
        params={"creation_id": creation_id, "access_token": ig_token}
    )
    publish_resp.raise_for_status()
    return f"https://instagram.com/p/{creation_id}"


def _upload_telegram(video_bytes: bytes) -> str:
    msg = TELEGRAM_BOT.send_video(
        chat_id=TELEGRAM_CHANNEL_ID,
        video=video_bytes,
        supports_streaming=True
    )
    return f"https://t.me/{TELEGRAM_CHANNEL_USERNAME}/{msg.message_id}"


def publish_draft(task_id: str) -> list[str]:
    file_path = f"/tmp/{task_id}.mp4"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Draft {task_id} not found.")
    with open(file_path, 'rb') as f:
        video_bytes = f.read()
    return upload_drafts(video_bytes, ['vk', 'tiktok', 'instagram', 'telegram'])
```python
import os
import requests
import base64
from telegram import Bot

# Initialize Telegram bot for channel uploads
TELEGRAM_BOT = Bot(token=os.getenv("BOT_TOKEN"))
AFFILIATE_ID_AE = os.getenv("AFFILIATE_ID_AE")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")


def _append_affiliate(url: str) -> str:
    sep = '&' if '?' in url else '?'
    return f"{url}{sep}aff_id={AFFILIATE_ID_AE}"


def upload_drafts(video_bytes: bytes, platforms: list[str]) -> list[str]:
    links = []
    for p in platforms:
        if p == 'vk':
            links.append(_upload_vk(video_bytes))
        elif p == 'tiktok':
            links.append(_upload_tiktok(video_bytes))
        elif p == 'instagram':
            links.append(_upload_instagram(video_bytes))
        elif p == 'telegram':
            links.append(_upload_telegram(video_bytes))
    return links


def _upload_vk(video_bytes: bytes) -> str:
    vk_token = os.getenv("VK_TOKEN")
    save_resp = requests.get(
        "https://api.vk.com/method/video.save",
        params={"access_token": vk_token, "v": "5.131"}
    ).json()
    upload_url = save_resp['response']['upload_url']
    files = {"video_file": ("video.mp4", video_bytes, "video/mp4")}
    upload_resp = requests.post(upload_url, files=files)
    upload_resp.raise_for_status()
    info = upload_resp.json()
    owner = info['owner_id']; vid = info['video_id']
    return f"https://vk.com/video{owner}_{vid}"


def _upload_tiktok(video_bytes: bytes) -> str:
    ttoken = os.getenv("TIKTOK_TOKEN")
    url = "https://open.tiktokapis.com/v1/video/upload"
    headers = {"Authorization": f"Bearer {ttoken}"}
    files = {"video": ("video.mp4", video_bytes, "video/mp4")}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json().get('data', {}).get('share_url', '')


def _upload_instagram(video_bytes: bytes) -> str:
    ig_token = os.getenv("IG_TOKEN")
    ig_user = os.getenv("IG_USER_ID")
    media_resp = requests.post(
        f"https://graph.facebook.com/v15.0/{ig_user}/media",
        params={"access_token": ig_token},
        files={"video_file": ("video.mp4", video_bytes, "video/mp4")}
    )
    media_resp.raise_for_status()
    creation_id = media_resp.json().get('id')
    publish_resp = requests.post(
        f"https://graph.facebook.com/v15.0/{ig_user}/media_publish",
        params={"creation_id": creation_id, "access_token": ig_token}
    )
    publish_resp.raise_for_status()
    return f"https://instagram.com/p/{creation_id}"


def _upload_telegram(video_bytes: bytes) -> str:
    msg = TELEGRAM_BOT.send_video(
        chat_id=TELEGRAM_CHANNEL_ID,
        video=video_bytes,
        supports_streaming=True
    )
    channel = os.getenv("TELEGRAM_CHANNEL_USERNAME")
    return f"https://t.me/{channel}/{msg.message_id}"


def publish_draft(task_id: str) -> list[str]:
    file_path = f"/tmp/{task_id}.mp4"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Draft {task_id} not found.")
    with open(file_path, 'rb') as f:
        video_bytes = f.read()
    return upload_drafts(video_bytes, ['vk','tiktok','instagram','telegram'])
```python
import os


def upload_drafts(video_bytes: bytes, platforms: list[str]) -> list[str]:
    links = []
    for p in platforms:
        # TODO: call each platform's API
        links.append(f"https://{p}.example.com/post/1234")
    return links


def publish_draft(task_id: str) -> list[str]:
    # fetch draft by task_id from storage
    video = b"..."
    return upload_drafts(video, ["vk", "instagram", "tiktok", "telegram"])


def fetch_stats() -> dict:
    # TODO: query database for stats
    return {'clicks': 1200, 'ctr': 5.4, 'sales': 80}