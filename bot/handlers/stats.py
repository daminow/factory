from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.upload import fetch_stats


async def cmd_stats(message: types.Message):
    data = fetch_stats()
    text = (
        f"📊 Статистика\n"
        f"• 🖱️ Клики: {data['clicks']}\n"
        f"• 📈 CTR: {data['ctr']}%\n"
        f"• 💰 Продажи: {data['sales']}"
    )
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔥 Тренды", callback_data="menu:trends"),
        InlineKeyboardButton("🏠 Меню", callback_data="menu:home"),
    )
    await message.reply(text, reply_markup=kb)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_stats, commands=["stats"])