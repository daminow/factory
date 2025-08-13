import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from bot.handlers import start, help, new, trends, approve, schedule, stats, settings
from bot.handlers import callbacks
from bot.middlewares.auth import RoleMiddleware


def main() -> None:
    env = os.getenv
    bot_token = env("BOT_TOKEN")
    redis_url = env("REDIS_URL")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set")
    if not redis_url:
        raise RuntimeError("REDIS_URL is not set")

    storage = RedisStorage2.from_url(redis_url)
    bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)

    admin_id = env("ADMIN_TELEGRAM_ID")
    if not admin_id:
        raise RuntimeError("ADMIN_TELEGRAM_ID is not set")
    dp.middleware.setup(RoleMiddleware(admin_id=int(admin_id)))

    # Register command handlers
    start.register(dp)
    help.register(dp)
    new.register(dp)
    trends.register(dp)
    approve.register(dp)
    schedule.register(dp)
    stats.register(dp)
    settings.register(dp)
    callbacks.register(dp)

    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()

