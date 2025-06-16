import os
from celery import Celery
from core.scraper import scrape_product
from core.ai import (
    gpt4o_mini,
    elevenlabs_tts,
    heygen_video,
    whisper_transcribe,
    capcut_compose
)
from core.upload import upload_drafts, publish_draft
from datetime import datetime

# Initialize Celery
broker_url = os.getenv("REDIS_URL")
app = Celery("tasks", broker=broker_url)

@app.task
def generate_creative(url: str, lang: str, platforms: list[str]):
    product = scrape_product(url)
    prompt = f"Сгенерируй сценарий видео для товара '{product['title']}' на русском языке."
    script = gpt4o_mini(prompt)
    audio_bytes = elevenlabs_tts(script, "ru")
    raw_video = heygen_video(audio_bytes, product['images'])
    captions = whisper_transcribe(audio_bytes)
    final_video = capcut_compose(raw_video, captions)
    file_path = f"/tmp/{app.current_task.request.id}.mp4"
    with open(file_path, 'wb') as f:
        f.write(final_video)
    return upload_drafts(final_video, platforms)

@app.task
def schedule_publish(task_id: str, publish_iso: str):
    publish_dt = datetime.fromisoformat(publish_iso)
    publish_task.apply_async((task_id,), eta=publish_dt)

@app.task
def publish_task(task_id: str):
    return publish_draft(task_id)
```python
import os
from celery import Celery
from core.scraper import scrape_product
from core.ai import (
    gpt4o_mini,
    elevenlabs_tts,
    heygen_video,
    whisper_transcribe,
    capcut_compose
)
from core.upload import upload_drafts
from datetime import datetime

# Initialize Celery
broker_url = os.getenv("REDIS_URL")
app = Celery("tasks", broker=broker_url)

@app.task
def generate_creative(url: str, lang: str, platforms: list[str]):
    # Получаем данные товара
    product = scrape_product(url)
    # Генерируем сценарий на русском языке
    prompt = f"Сгенерируй сценарий видео для товара '{product['title']}' на русском языке."
    script = gpt4o_mini(prompt)
    # Озвучка на русском (ru)
    audio_bytes = elevenlabs_tts(script, "ru")
    # Генерация видео
    raw_video = heygen_video(audio_bytes, product['images'])
    # Транскрипция (субтитры)
    captions = whisper_transcribe(audio_bytes)
    # Сборка финального видео
    final_video = capcut_compose(raw_video, captions)
    # Сохранение локально
    file_path = f"/tmp/{app.current_task.request.id}.mp4"
    with open(file_path, 'wb') as f:
        f.write(final_video)
    # Возвращаем ссылки на черновики
    return upload_drafts(final_video, platforms)

@app.task
def schedule_publish(task_id: str, publish_iso: str):
    # Планируем публикацию по точному времени
    publish_dt = datetime.fromisoformat(publish_iso)
    publish_task.apply_async((task_id,), eta=publish_dt)

@app.task
def publish_task(task_id: str):
    # Функция публикации черновика
    from core.upload import publish_draft as _publish
    return _publish(task_id)
```python
import os
from celery import Celery
from core.scraper import scrape_product
from core.ai import (
    gpt4o_mini,
    elevenlabs_tts,
    heygen_video,
    whisper_transcribe,
    capcut_compose
)
from core.upload import upload_drafts
from datetime import datetime

# Initialize Celery
broker_url = os.getenv("REDIS_URL")
app = Celery("tasks", broker=broker_url)

@app.task
def generate_creative(url: str, lang: str, platforms: list[str]):
    product = scrape_product(url)
    prompt = f"Generate video script for '{product['title']}' in {lang}"
    script = gpt4o_mini(prompt)
    audio_bytes = elevenlabs_tts(script, lang)
    raw_video = heygen_video(audio_bytes, product['images'])
    captions = whisper_transcribe(audio_bytes)
    final_video = capcut_compose(raw_video, captions)
    # Save locally
    file_path = f"/tmp/{app.current_task.request.id}.mp4"
    with open(file_path, 'wb') as f:
        f.write(final_video)
    # Upload drafts
    return upload_drafts(final_video, platforms)

@app.task
def schedule_publish(task_id: str, publish_iso: str):
    publish_dt = datetime.fromisoformat(publish_iso)
    # Schedule actual publishing
    publish_task.apply_async((task_id,), eta=publish_dt)

@app.task
def publish_task(task_id: str):
    from core.upload import publish_draft as _publish
    return _publish(task_id)
```python
import os
from celery import Celery
from core.scraper import scrape_product
from core.ai import gpt4o_mini, elevenlabs_tts, heygen_video, whisper_transcribe, capcut_compose
from core.upload import upload_drafts


env = os.getenv
broker = env("REDIS_URL")
celery = Celery(__name__, broker=broker)

@celery.task
async def generate_creative(url: str, lang: str, platforms: list[str]):
    product = scrape_product(url)
    script = gpt4o_mini(f"Generate script for {product['title']} in {lang}")
    audio = elevenlabs_tts(script, lang)
    raw_video = heygen_video(audio, product['images'])
    captions = whisper_transcribe(audio)
    final_video = capcut_compose(raw_video, captions)
    return upload_drafts(final_video, platforms)

@celery.task
def schedule_publish(task_id: str, publish_time):
    # TODO: schedule using APScheduler or celery beat
    pass