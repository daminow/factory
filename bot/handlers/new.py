import re
from aiogram import types, Dispatcher
from core.scraper import scrape_product
from celery import uuid
from workers.tasks import generate_creative

URL_REGEX = re.compile(r"https?://[\w./?=&-]+")

async def cmd_new(message: types.Message):
    args = message.get_args()
    if not args or not URL_REGEX.match(args):
        return await message.reply("Укажите корректный URL: /new <URL>")
    task_id = uuid()
    # schedule Celery task
    generate_creative.apply_async((args, "RU", ["vk", "tiktok", "instagram", "telegram"]), task_id=task_id)
    await message.reply(f"Задача на генерацию видео принята: ID {task_id}")


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_new, commands=["new"])