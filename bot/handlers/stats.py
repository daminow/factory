from aiogram import types, Dispatcher
from core.upload import fetch_stats

async def cmd_stats(message: types.Message):
    data = fetch_stats()
    text = (
        f"Clicks: {data['clicks']}\n"
        f"CTR: {data['ctr']}%\n"
        f"Sales: {data['sales']}"
    )
    await message.reply(text)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_stats, commands=["stats"])