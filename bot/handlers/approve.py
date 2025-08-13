from aiogram import types, Dispatcher
from core.upload import publish_draft


async def cmd_approve(message: types.Message):
    args = message.get_args().split()
    if not args:
        return await message.reply("✍️ Укажите ID черновика: /approve <ID>")
    task_id = args[0]
    try:
        links = publish_draft(task_id)
    except FileNotFoundError:
        return await message.reply("❌ Черновик не найден. Убедитесь, что задача завершилась. ID: " + task_id)
    except Exception as e:
        return await message.reply(f"⚠️ Ошибка публикации: {e}")
    await message.reply("✅ Опубликовано:\n" + "\n".join(links))


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_approve, commands=["approve"])