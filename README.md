## English

### Automated Creative Factory (Telegram + Celery + AI)

End‑to‑end automated pipeline: scrape a product, write script, synthesize voice, assemble a vertical video with subtitles, save a draft, publish instantly or schedule — all controlled from a Telegram bot. Admin‑only access via middleware.

### Features

- Video generation: gTTS/ElevenLabs TTS, video assembly (moviepy), subtitles (OpenAI Whisper if key is provided; graceful fallback).
- Trends discovery: AliExpress Affiliate API (if `AFFILIATE_APP_KEY` is set), otherwise empty list.
- Telegram UX: commands and inline buttons with emojis; quick actions for Approve/Schedule/Menu.
- Background jobs: Celery (Redis broker/backend), shared volume `/drafts`.
- Admin notifications: when a draft is ready and after publish.

### Stack

- Python 3.12, aiogram 2.x, Celery 5, Redis, moviepy, gTTS, requests
- Docker + Docker Compose

### Repository structure

```
factory/
├─ bot/
│  ├─ handlers/          # Commands and callbacks
│  ├─ middlewares/       # Admin‑only access
│  └─ main.py            # Bot entrypoint
├─ core/                 # Scraper, AI, pipeline, uploaders, config, notifier
├─ workers/              # Celery tasks (worker + beat in compose)
├─ Dockerfile.bot
├─ Dockerfile.workers
├─ docker-compose.yml
└─ setup_vm.sh           # One‑shot provisioning on a new VM
```

### Quick start (fresh Ubuntu VM)

1. Put your bot token and admin id at hand.
2. Run the installer (it will install Docker, create `.env`, build and start):

```bash
bash setup_vm.sh
```

3. Talk to your bot from the `ADMIN_TELEGRAM_ID` account and send `/start`.

### Manual run (if you already have Docker)

```bash
# Create .env (see below)
docker compose build
docker compose up -d
```

### Environment (.env example)

```env
BOT_TOKEN=123456:ABCDEF
ADMIN_TELEGRAM_ID=111111111
REDIS_URL=redis://redis:6379/0

# Platforms and affiliate (optional)
PLATFORMS=vk,tiktok,instagram,telegram
AFFILIATE_APP_KEY=

# AI keys (optional)
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
HEYGEN_TOKEN=
CAPCUT_TOKEN=

# Video params (optional)
VIDEO_FPS=24
VIDEO_DURATION_DEFAULT=15

# Telegram publishing (channel)
TELEGRAM_CHANNEL_ID=
TELEGRAM_CHANNEL_USERNAME=

# Shared volume path (do not change in compose)
DRAFTS_DIR=/drafts
```

### Bot commands and inline UI

- /new <URL> — start generation; you will receive inline buttons: Approve, Schedule, Menu.
- /approve <ID> — force publish a draft by id.
- /schedule <ID> DD.MM HH:MM — schedule publish; year is auto‑filled; past times roll to next year.
- /trends — top trends (if affiliate API key is set).
- /stats — simple stats placeholder.
- /settings — inline selection for langs/platforms (demo).

### Operations

- Worker logs: `docker compose logs -f worker`
- Bot logs: `docker compose logs -f bot`
- Stop: `docker compose down`

### Production notes

- Replace upload placeholders in `core/upload.py` with real platform APIs.
- Prefer object storage (S3/MinIO) over local volumes; keep metadata in DB/Redis.
- Add observability (Sentry/OTel), structured logs, rate‑limits.
- Celery: tune retries/queues; deduplicate by product URL.

---

## Русский

### Автоматизированная фабрика креативов (Telegram + Celery + AI)

Конвейер от товара до публикации: скрейпинг, сценарий, TTS, сборка вертикального видео с субтитрами, черновик и публикация/расписание — управление через Telegram бота. Доступ только администратору.

### Возможности

- Генерация видео: gTTS/ElevenLabs TTS, сборка (moviepy), субтитры (OpenAI Whisper при наличии ключа; есть fallback).
- Тренды: AliExpress Affiliate API (если задан `AFFILIATE_APP_KEY`).
- Удобный UX: инлайн‑кнопки с эмодзи; быстрые действия — Опубликовать/Запланировать/Меню.
- Фоновые задачи: Celery (Redis broker и backend), общий том `/drafts`.
- Уведомления администратору: по готовности черновика и после публикации.

### Стек

- Python 3.12, aiogram 2.x, Celery 5, Redis, moviepy, gTTS, requests
- Docker + Docker Compose

### Структура

```
factory/
├─ bot/                  # Telegram‑бот и хендлеры
├─ core/                 # Скрейпер, AI, пайплайн, публикации, конфиг, уведомления
├─ workers/              # Задачи Celery
├─ Dockerfile.bot
├─ Dockerfile.workers
├─ docker-compose.yml
└─ setup_vm.sh           # Установка на чистой VM
```

### Быстрый старт (чистая Ubuntu VM)

1. Подготовьте токен бота и ID админа.
2. Запустите установщик (поставит Docker, создаст `.env`, соберёт и запустит):

```bash
bash setup_vm.sh
```

3. Напишите боту `/start` с аккаунта `ADMIN_TELEGRAM_ID`.

### Ручной запуск (если Docker уже есть)

```bash
# Создайте .env (см. ниже)
docker compose build
docker compose up -d
```

### Переменные окружения (.env пример)

```env
BOT_TOKEN=123456:ABCDEF
ADMIN_TELEGRAM_ID=111111111
REDIS_URL=redis://redis:6379/0

# Платформы и партнёрка (опционально)
PLATFORMS=vk,tiktok,instagram,telegram
AFFILIATE_APP_KEY=

# AI ключи (опционально)
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
HEYGEN_TOKEN=
CAPCUT_TOKEN=

# Видео‑параметры (опционально)
VIDEO_FPS=24
VIDEO_DURATION_DEFAULT=15

# Публикация в Telegram (канал)
TELEGRAM_CHANNEL_ID=
TELEGRAM_CHANNEL_USERNAME=

# Общий том (не менять в compose)
DRAFTS_DIR=/drafts
```

### Команды бота и инлайн UI

- /new <URL> — генерация; придут кнопки: Опубликовать, Запланировать, Меню.
- /approve <ID> — принудительная публикация черновика по ID.
- /schedule <ID> DD.MM HH:MM — планирование; год подставляется автоматически; прошлое — перенос на следующий год.
- /trends — тренды (если задан ключ партнёрки).
- /stats — заглушка статистики.
- /settings — выбор языков и платформ (демо).

### Эксплуатация

- Логи воркера: `docker compose logs -f worker`
- Логи бота: `docker compose logs -f bot`
- Остановка: `docker compose down`

### Примечания для продакшена

- Заменить заглушки публикаций в `core/upload.py` на реальные API платформ.
- Хранение: MinIO/S3 вместо локального тома; метаданные — Redis/БД.
- Наблюдаемость: Sentry/OTel, структурные логи, rate‑limits.
- Celery: ретраи/очереди; дедупликация по URL товара.

### Лицензия

MIT
