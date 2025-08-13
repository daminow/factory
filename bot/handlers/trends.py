from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.scraper import get_top_trends


async def cmd_trends(message: types.Message):
    trends = get_top_trends()
    if not trends:
        return await message.reply("📉 Нет данных по трендам сейчас.")
    text = "🔥 Топ-10 трендов за 24ч:\n" + "\n".join(
        f"{i+1}. {p['name']} — 🛒 {p['orders']} заказов, ⭐ {p['rating']}"
        for i, p in enumerate(trends)
    )
    kb = InlineKeyboardMarkup(row_width=1)
    for p in trends:
        kb.add(InlineKeyboardButton(f"🔗 {p['name'][:40]}…", url=p['url']))
    kb.add(InlineKeyboardButton("🏠 Меню", callback_data="menu:home"))
    await message.reply(text, reply_markup=kb)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_trends, commands=["trends"])