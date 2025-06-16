from aiogram import types, Dispatcher
from core.upload import publish_draft

async def cmd_approve(message: types.Message):
    args = message.get_args().split()
    if not args:
        return await message.reply("Укажите ID черновика: /approve <ID>")
    task_id = args[0]
    links = publish_draft(task_id)
    await message.reply("Опубликовано:\n" + "\n".join(links))


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_approve, commands=["approve"])