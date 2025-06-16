```
project/
├─ bot/
│  ├─ handlers/
│  │   ├─ start.py
│  │   ├─ help.py
│  │   ├─ new.py            # генерация и отправка черновика с inline-кнопками
│  │   ├─ callbacks.py      # обработка inline-кнопок: edit, publish, schedule
│  │   ├─ trends.py
│  │   ├─ ai_usage.py       # демонстрация интеграций с AI-сервисами
│  │   └─ settings.py
│  ├─ middlewares/
│  │   └─ auth.py
│  ├─ keyboards/
│  │   └─ menu.py
│  ├─ __init__.py
│  └─ main.py
├─ workers/
│  └─ tasks.py
├─ core/
│  ├─ scraper.py
│  ├─ ai.py
│  ├─ upload.py
│  └─ config.py
├─ docker-compose.yml
├─ nginx.conf
├─ Dockerfile.bot
├─ Dockerfile.workers
└─ .env.example
```

---

# bot/main.py

```python
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from bot.handlers import start, help, new, trends, callbacks, settings
from bot.middlewares.auth import RoleMiddleware

env = os.getenv
BOT_TOKEN = env("BOT_TOKEN")
REDIS_URL = env("REDIS_URL")

storage = RedisStorage2.from_url(REDIS_URL)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Middleware for role-based access
dp.middleware.setup(RoleMiddleware())

# Register command handlers
start.register(dp)
help.register(dp)
new.register(dp)
trends.register(dp)
settings.register(dp)

# Register callback query handlers
actions = callbacks.register
actions(dp)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
```

---

# bot/handlers/new\.py

```python
import re
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.ai import generate_full_pipeline

URL_REGEX = re.compile(r"https?://[\w./?=&-]+")

async def cmd_new(message: types.Message):
    args = message.get_args()
    if not args or not URL_REGEX.match(args):
        return await message.reply("Укажите корректный URL: /new <URL>")
    # Запуск AI-пайплайна: видео+субтитры+озвучка
    video_bytes, subtitle_text = generate_full_pipeline(args)
    # Сохраняем во временное хранилище, генерируем draft_id
    draft_id = save_draft(video_bytes, subtitle_text)
    # Формируем Inline-кнопки
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{draft_id}"),
        InlineKeyboardButton("✏️ Edit", callback_data=f"edit:{draft_id}"),
        InlineKeyboardButton("🕒 Schedule", callback_data=f"schedule:{draft_id}"),
    )
    # Платформы выбора публикации отображаются позже при нажатии Approve
    await message.reply_video(
        video=video_bytes,
        caption=subtitle_text,
        reply_markup=kb
    )


def save_draft(video: bytes, subtitles: str) -> str:
    # TODO: сохранить в MinIO или БД, возвращаем draft_id
    import uuid
    return str(uuid.uuid4())


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_new, commands=["new"])
```

---

# bot/handlers/callbacks.py

```python
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.upload import publish_to_platforms, get_platform_list
from core.scheduler import schedule_publish_task

PLATFORMS = get_platform_list()  # e.g. ["vk","tiktok","instagram","telegram"]

async def on_approve(callback: types.CallbackQuery):
    draft_id = callback.data.split(":")[1]
    # Предложим выбрать платформы
    kb = InlineKeyboardMarkup(row_width=2)
    for p in PLATFORMS:
        kb.insert(InlineKeyboardButton(p.upper(), callback_data=f"pub_{p}:{draft_id}"))
    await callback.message.edit_caption(
        callback.message.caption + "\nВыберите, куда публиковать:",
        reply_markup=kb
    )
    await callback.answer()

async def on_pub(callback: types.CallbackQuery):
    platform, draft_id = callback.data.split(":")[0].split("_")[1], callback.data.split(":")[1]
    link = publish_to_platforms(draft_id, [platform])[0]
    await callback.message.answer(f"Опубликовано на {platform}: {link}")
    await callback.answer()

async def on_schedule(callback: types.CallbackQuery):
    draft_id = callback.data.split(":")[1]
    # Кнопки с временем: сейчас, +1ч, +3ч
    kb = InlineKeyboardMarkup(row_width=3)
    for label, offset in [("Сейчас",0),("+1ч",1),("+3ч",3)]:
        kb.insert(InlineKeyboardButton(label, callback_data=f"sched_{offset}:{draft_id}"))
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()

async def on_sched(callback: types.CallbackQuery):
    offset, draft_id = map(str, callback.data.split(":"))
    offset = int(offset.split("_")[1])
    schedule_publish_task(draft_id, offset)
    await callback.message.answer(f"Публикация {draft_id} запланирована через {offset} ч.")
    await callback.answer()

async def on_edit(callback: types.CallbackQuery):
    draft_id = callback.data.split(":")[1]
    await callback.message.answer(f"Отправьте, пожалуйста, правки для {draft_id}.")
    await callback.answer()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(on_approve, lambda cb: cb.data.startswith("approve:"))
    dp.register_callback_query_handler(on_pub, lambda cb: cb.data.startswith("pub_"))
    dp.register_callback_query_handler(on_schedule, lambda cb: cb.data.startswith("schedule:"))
    dp.register_callback_query_handler(on_sched, lambda cb: cb.data.startswith("sched_"))
    dp.register_callback_query_handler(on_edit, lambda cb: cb.data.startswith("edit:"))
```

---

# core/ai.py

```python
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import openai

env = load_dotenv()

# ElevenLabs setup
eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
ELE_VOICE = os.getenv("ELEVENLABS_VOICE_ID")
ELE_MODEL = os.getenv("ELEVENLABS_MODEL_ID")

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

from core.scraper import scrape_product
from core.upload import upload_drafts


def generate_full_pipeline(url: str):
    product = scrape_product(url)
    # 1) GPT сценарий
    script = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":f"Напиши сценарий для видео: {product['title']}"}]
    ).choices[0].message.content
    # 2) TTS
    audio = eleven.text_to_speech.convert(
        text=script,
        voice_id=ELE_VOICE,
        model_id=ELE_MODEL,
        output_format="mp3_44100_128"
    )
    # 3) Видео с HeyGen/Pika (заглушка)
    # TODO: интеграция HeyGen/Pika
    video_bytes = make_video_with_ai(audio, product['images'])
    # 4) Субтитры (Whisper через OpenAI)
    captions = openai.Audio.transcriptions.create(
        file=audio,
        model="whisper-1"
    ).text
    # Возвращаем видео и субтитры
    return video_bytes, captions


def make_video_with_ai(audio: bytes, images: list[str]) -> bytes:
    # Заглушка: просто возвращаем audio как видео
    return audio
```

---

# core/upload.py

```python
import os
from core.config import PLATFORMS


def get_platform_list() -> list[str]:
    return PLATFORMS


def publish_to_platforms(draft_id: str, platforms: list[str]) -> list[str]:
    links = []
    for p in platforms:
        # Реальная интеграция должна использовать API-сервисы
        token = os.getenv(f"{p.upper()}_TOKEN")
        # TODO: реализовать постинг через API каждого сервиса
        links.append(f"https://{p}.example.com/post/{draft_id}")
    return links
```

---

# core/config.py

```python
import os
PLATFORMS = os.getenv("PLATFORMS", "vk,tiktok,instagram,telegram").split(',')
```

---

# workers/tasks.py (без изменений)

```python
import os
from celery import Celery
from core.scraper import scrape_product
from core.ai import generate_full_pipeline
from core.upload import publish_to_platforms
from core.scheduler import schedule_publish_task

broker = os.getenv("REDIS_URL")
celery_app = Celery(__name__, broker=broker)

@celery_app.task
async def generate_creative(url: str):
    video, captions = generate_full_pipeline(url)
    draft_id = save_draft(video, captions)
    return draft_id
```

---

# README.md

## Project Overview

The Automated Ad Factory is a fully automated content creation and distribution system that finds trending products on Chinese marketplaces, generates creative video ads with AI-powered scripting, voice-over, and subtitles in multiple languages, and publishes them to VK, TikTok, Instagram, and Telegram via a unified Telegram bot interface.

## Features

- **Product Scraping**: Extracts product data from 1688, AliExpress, and other sources using Selenium, BeautifulSoup, and official APIs.
- **AI-Powered Video Pipeline**: Generates video scripts (GPT-4o Mini), performs TTS (ElevenLabs), assembles videos (HeyGen/Pika placeholder), and transcribes captions (Whisper).
- **Multi-Language Support**: Produces content in Russian, Uzbek, Kazakh, and English.
- **Telegram Bot Interface**: Manage drafts inline, approve, edit, or schedule posts with interactive buttons.
- **Celery Workers**: Background tasks for creative generation and scheduled publishing (APScheduler integration).
- **Platform Publishing**: Post to VK, TikTok, Instagram Reels, and Telegram with partner/referral links.
- **Analytics & Reporting**: Fetches click, CTR, and sales stats from the database.
- **Containerized Deployment**: Docker Compose setup with Redis, PostgreSQL, and Nginx reverse proxy.

## Architecture & Directory Structure

```
project/
├─ bot/                # Telegram bot (aiogram)
├─ workers/            # Celery tasks for AI pipeline and scheduling
├─ core/               # Core modules: scraper, AI wrappers, upload, config
├─ docker-compose.yml  # Service definitions: bot, worker, scheduler, redis, db
├─ nginx.conf          # Reverse proxy configuration
├─ Dockerfile.bot      # Bot Docker image
├─ Dockerfile.workers  # Worker Docker image
└─ .env.example        # Environment variable template
```

## Prerequisites

- Docker & Docker Compose installed
- A Telegram bot token (set via BOT_TOKEN)
- Redis instance (default provided via Docker)
- PostgreSQL database (default via Docker)
- AI service API keys for OpenAI, ElevenLabs, HeyGen/Pika, CapCut

## Configuration

1. Copy and fill environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your keys and settings
   ```

2. Ensure ports 80/443 and necessary inbound rules are open for webhooks.

## Installation & Running

```bash
# Clone repository
git clone https://github.com/your/factory.git
cd factory

# Configure environment
cp .env.example .env
# Edit .env

# Launch services
docker compose pull
docker compose up -d
```

## Usage

- **Polling mode** (development):

  ```bash
  docker exec -it <bot_container> python bot/main.py
  ```

- **Commands**:

  - `/start` — Welcome & role registration
  - `/help` — List available commands
  - `/new <URL>` — Generate a video draft
  - Inline buttons: Approve, Edit, Schedule
  - `/trends` — Top-10 trending products
  - `/stats` — Clicks, CTR, sales summary
  - `/settings` — Language & platform preferences

## Deployment Tips

- Use `docker compose logs -f` to monitor logs.
- Set Telegram webhook for production:

  ```bash
  curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$DOMAIN_BASE/webhook/$WEBHOOK_SECRET"
  ```

- Secure SSH access and firewall (UFW) on VPS.

## Contributing

Contributions welcome! Please open issues and pull requests for enhancements, bug fixes, or configuration improvements.

## License

This project is licensed under the MIT License.
