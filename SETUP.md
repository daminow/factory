# Быстрый старт и обслуживание

## 1) Требования
- Docker, Docker Compose
- Телеграм-бот (токен)
- Telegram ID администратора, канал (для публикаций)

## 2) Настройка окружения
Создайте `.env` в корне проекта со значениями:

```
BOT_TOKEN=xxxx:yyyy
ADMIN_TELEGRAM_ID=123456789
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_CHANNEL_USERNAME=your_channel

REDIS_URL=redis://redis:6379/0
DRAFTS_DIR=/drafts
PLATFORMS=telegram

OPENAI_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
HEYGEN_TOKEN=
CAPCUT_TOKEN=

VIDEO_FPS=24
VIDEO_DURATION_DEFAULT=15

AFFILIATE_APP_KEY=
```

## 3) Сборка и запуск
```
make build
make up
```
Логи:
```
make logs
```

## 4) Проверка
- Напишите боту `/start` с аккаунта администратора
- `/new <url>` — запускает генерацию
- по готовности придёт уведомление; опубликовать: кнопка или `/approve <id>`

## 5) Обслуживание
- Обновление зависимостей: изменить `requirements.txt` → `make build && make up`
- Резервные копии: перенос `/drafts` тома; для прод — используйте S3/MinIO
- Мониторинг: добавьте Sentry/OTel, Prometheus (см. README)

## 6) Тонкая настройка
- Для лучших голосов используйте ELEVENLABS_API_KEY
- Для автоматических субтитров — OPENAI_API_KEY (Whisper)
- Для удалённой генерации видео — HEYGEN_TOKEN, для компоновки — CAPCUT_TOKEN

## 7) CI/CD (опционально)
- Добавьте GitHub Actions workflow: build, lint, push
- pre-commit hooks (black/ruff) по вкусу
