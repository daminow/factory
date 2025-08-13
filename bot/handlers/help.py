from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def cmd_help(message: types.Message):
    text = (
        "❓ Помощь\n\n"
        "Команды:\n"
        "• 🎬 /new <URL> — сгенерировать черновик\n"
        "• ✅ /approve <ID> — опубликовать черновик\n"
        "• 🗓️ /schedule <ID> DD.MM HH:MM — запланировать публикацию\n"
        "• 📈 /trends — тренды за 24ч\n"
        "• 📊 /stats — статистика\n"
        "• ⚙️ /settings — настройки\n"
        "• 👋 /start — приветствие"
    )
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🎬 Создать черновик", callback_data="menu:new"),
        InlineKeyboardButton("🔥 Тренды", callback_data="menu:trends"),
        InlineKeyboardButton("📊 Статистика", callback_data="menu:stats"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="menu:settings"),
    )
    await message.reply(text, reply_markup=kb)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_help, commands=["help"])