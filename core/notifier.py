import os
import requests


BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_text(chat_id: int, text: str) -> None:
    if not BOT_TOKEN:
        return
    try:
        requests.post(
            f"{API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
    except Exception:
        pass


def send_menu(chat_id: int, text: str, buttons: list[list[dict]]) -> None:
    if not BOT_TOKEN:
        return
    try:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"inline_keyboard": buttons},
        }
        # prevent sending overly long keyboard or text
        if len(text) > 4000:
            payload["text"] = text[:3990] + "…"
        if len(buttons) > 8:
            payload["reply_markup"]["inline_keyboard"] = buttons[:8]
        requests.post(f"{API_URL}/sendMessage", json=payload, timeout=15)
    except Exception:
        pass

