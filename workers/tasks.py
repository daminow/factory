import os
from celery import Celery
from celery.utils.log import get_task_logger
from core.ai_pipeline import generate_video_pipeline
from datetime import datetime
from core.notifier import send_text, send_menu
from core.upload import publish_draft


broker_url = os.getenv("REDIS_URL")
app = Celery("tasks", broker=broker_url, backend=broker_url)
app.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    enable_utc=True,
    timezone="UTC",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_transport_options={"visibility_timeout": 3600},
)
logger = get_task_logger(__name__)

DRAFTS_DIR = os.getenv("DRAFTS_DIR", "/drafts")


@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_creative(self, url: str, lang: str, platforms: list[str]):
    final_video, captions, _ = generate_video_pipeline(url, lang)

    task_id = self.request.id
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    try:
        os.chmod(DRAFTS_DIR, 0o700)
    except Exception:
        pass
    file_path = os.path.join(DRAFTS_DIR, f"{task_id}.mp4")
    with open(file_path, "wb") as f:
        f.write(final_video)
    try:
        os.chmod(file_path, 0o600)
    except Exception:
        pass
    # сохраняем субтитры рядом, чтобы использовать как caption при публикации
    try:
        captions_path = os.path.join(DRAFTS_DIR, f"{task_id}.txt")
        with open(captions_path, "w", encoding="utf-8") as cf:
            cf.write(captions or "")
        try:
            os.chmod(captions_path, 0o600)
        except Exception:
            pass
    except Exception as e:
        logger.warning("Failed to save captions for %s: %s", task_id, e)
    # уведомляем админа о готовности
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if admin_id:
        try:
            buttons = [
                [
                    {"text": "✅ Опубликовать", "callback_data": f"approve:{task_id}"},
                    {"text": "🗓️ Запланировать", "callback_data": f"schedule:{task_id}"},
                ],
                [
                    {"text": "🏠 Меню", "callback_data": "menu:home"},
                ],
            ]
            send_menu(int(admin_id), f"🧩 Черновик готов: {task_id}", buttons)
        except Exception:
            try:
                send_text(int(admin_id), f"🧩 Черновик готов: {task_id}")
            except Exception:
                pass
    return {"task_id": task_id, "status": "draft_saved"}


@app.task
def schedule_publish(task_id: str, publish_iso: str):
    publish_dt = datetime.fromisoformat(publish_iso)
    publish_task.apply_async((task_id,), eta=publish_dt)


@app.task
def publish_task(task_id: str):
    links = publish_draft(task_id)
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if admin_id:
        try:
            send_text(int(admin_id), "✅ Опубликовано:\n" + "\n".join(links))
        except Exception:
            pass
    return links

