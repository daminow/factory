import os
import requests

DRAFTS_DIR = os.getenv("DRAFTS_DIR", "/drafts")


def _upload_telegram(video_bytes: bytes, caption: str | None = None) -> str:
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHANNEL_ID")
    if not token or not chat_id:
        raise RuntimeError("Telegram publishing requires BOT_TOKEN and TELEGRAM_CHANNEL_ID in env")
    api = f"https://api.telegram.org/bot{token}/sendVideo"
    data = {
        "chat_id": chat_id,
        "supports_streaming": True,
        "disable_notification": False,
    }
    if caption:
        data["caption"] = caption[:1024]
    # Limit video size to avoid Telegram limits surprise (50MB+ is risky for bot API)
    if len(video_bytes) > 45 * 1024 * 1024:
        raise RuntimeError("Video too large for Telegram bot upload (>45MB)")
    files = {"video": ("video.mp4", video_bytes, "video/mp4")}
    resp = requests.post(api, data=data, files=files, timeout=120)
    resp.raise_for_status()
    j = resp.json()
    if not j.get("ok"):
        raise RuntimeError(str(j))
    msg = j["result"]
    username = os.getenv("TELEGRAM_CHANNEL_USERNAME") or (msg.get("chat", {}).get("username") or "")
    message_id = msg.get("message_id")
    if username:
        return f"https://t.me/{username}/{message_id}"
    return f"telegram:chat:{chat_id}:message:{message_id}"


def upload_drafts(video_bytes: bytes, platforms: list[str], caption: str | None = None) -> list[str]:
    links: list[str] = []
    for p in platforms:
        if p == "telegram":
            links.append(_upload_telegram(video_bytes, caption=caption))
        else:
            # Placeholder for other platforms; implement per API in prod
            links.append(f"https://{p}.example.com/post/1234")
    return links


def publish_draft(task_id: str) -> list[str]:
    file_path = os.path.join(DRAFTS_DIR, f"{task_id}.mp4")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Draft {task_id} not found.")
    with open(file_path, "rb") as f:
        video_bytes = f.read()
    # подхватываем подпись, если есть
    caption_path = os.path.join(DRAFTS_DIR, f"{task_id}.txt")
    caption = None
    if os.path.exists(caption_path):
        try:
            with open(caption_path, "r", encoding="utf-8") as cf:
                caption = cf.read().strip()
        except Exception:
            caption = None
    return upload_drafts(video_bytes, ["telegram"], caption=caption)  # минимум — публикация в Telegram


def fetch_stats() -> dict:
    # Заглушка статистики до интеграции с реальными источниками
    return {"clicks": 0, "ctr": 0.0, "sales": 0}