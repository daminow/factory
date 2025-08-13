from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎬 Создать черновик", callback_data="menu:new"),
        InlineKeyboardButton("🔥 Тренды", callback_data="menu:trends"),
        InlineKeyboardButton("📊 Статистика", callback_data="menu:stats"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="menu:settings"),
    )
    await message.reply(
        "👋 Привет! Это админ-бот автоматизированного завода креативов.\n"
        "Выберите действие ниже или используйте команды /help",
        reply_markup=kb,
    )


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"]) 

