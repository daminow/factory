from aiogram import types, Dispatcher
from core.scraper import get_top_trends

async def cmd_trends(message: types.Message):
    trends = get_top_trends()
    text = "#TOP-10 трендов за 24ч:\n" + "\n".join(
        f"{i+1}. {p['name']} — {p['orders']} orders, rating {p['rating']}"
        for i, p in enumerate(trends)
    )
    await message.reply(text)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_trends, commands=["trends"])