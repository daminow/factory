import re
from aiogram import types, Dispatcher
from celery import uuid
from workers.tasks import generate_creative
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


URL_REGEX = re.compile(r"https?://[\w./?=&-]+")


async def cmd_new(message: types.Message):
    args = message.get_args()
    if not args or not URL_REGEX.match(args):
        return await message.reply("Укажите корректный URL: /new <URL>")
    task_id = uuid()
    generate_creative.apply_async(
        (args, "RU", ["vk", "tiktok", "instagram", "telegram"]), task_id=task_id
    )
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Опубликовать", callback_data=f"approve:{task_id}"),
        InlineKeyboardButton("🗓️ Запланировать", callback_data=f"schedule:{task_id}"),
    )
    kb.add(
        InlineKeyboardButton("🏠 Меню", callback_data="menu:home"),
    )
    await message.reply(
        f"🧩 Задача на генерацию принята. ID: {task_id}. Когда будет готово, нажмите кнопку ниже или используйте команды: /approve {task_id} или /schedule {task_id} DD.MM HH:MM",
        reply_markup=kb,
    )


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_new, commands=["new"])