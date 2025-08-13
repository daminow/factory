import datetime
from aiogram import types, Dispatcher
from workers.tasks import schedule_publish


async def cmd_schedule(message: types.Message):
    parts = message.get_args().split()
    if len(parts) < 2:
        return await message.reply("✍️ Используйте: /schedule <ID> DD.MM HH:MM")
    task_id, dt = parts[0], " ".join(parts[1:])
    parsed = datetime.datetime.strptime(dt, "%d.%m %H:%M")
    now = datetime.datetime.now()
    dt_obj = parsed.replace(year=now.year)
    if dt_obj < now:
        dt_obj = dt_obj.replace(year=now.year + 1)
    schedule_publish.apply_async((task_id, dt_obj.isoformat()))
    await message.reply(f"🗓️ Публикация задачи {task_id} запланирована на {dt}")


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_schedule, commands=["schedule"])

