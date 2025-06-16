import datetime
from aiogram import types, Dispatcher
from workers.tasks import schedule_publish

async def cmd_schedule(message: types.Message):
    parts = message.get_args().split()
    if len(parts) < 2:
        return await message.reply("Используйте: /schedule <ID> DD.MM HH:MM")
    task_id, dt = parts[0], parts[1]
    dt_obj = datetime.datetime.strptime(dt, "%d.%m %H:%M")
    schedule_publish(task_id, dt_obj)
    await message.reply(f"Публикация задачи {task_id} запланирована на {dt}")


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, commands=["schedule"])