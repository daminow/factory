import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from middlewares.auth import RoleMiddleware

# Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
bot = Bot(token=BOT_TOKEN)
storage = RedisStorage2.from_url(REDIS_URL)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(RoleMiddleware())

# Callback factories
enum MenuActions:
    NEW = "new"
    TRENDS = "trends"
    APPROVE = "approve"
    SCHEDULE = "schedule"
    STATS = "stats"
    SETTINGS = "settings"

menu_cb = CallbackData("menu", "action")
cancel_cb = CallbackData("cancel", "action")

# States
class NewState(StatesGroup):
    url = State()

class ApproveState(StatesGroup):
    task_id = State()

class ScheduleState(StatesGroup):
    data = State()

# Main menu
def main_menu_markup():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.insert(types.InlineKeyboardButton("Новый товар", callback_data=menu_cb.new(action=MenuActions.NEW)))
    kb.insert(types.InlineKeyboardButton("Тренды", callback_data=menu_cb.new(action=MenuActions.TRENDS)))
    kb.insert(types.InlineKeyboardButton("Утвердить", callback_data=menu_cb.new(action=MenuActions.APPROVE)))
    kb.insert(types.InlineKeyboardButton("Запланировать", callback_data=menu_cb.new(action=MenuActions.SCHEDULE)))
    kb.insert(types.InlineKeyboardButton("Статистика", callback_data=menu_cb.new(action=MenuActions.STATS)))
    kb.insert(types.InlineKeyboardButton("Настройки", callback_data=menu_cb.new(action=MenuActions.SETTINGS)))
    return kb

async def show_main_menu(chat_id: int):
    await bot.send_message(chat_id, "Выберите действие:", reply_markup=main_menu_markup())

# Start handler
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    token = message.get_args().strip()
    if not token:
        return await message.reply("Используйте: /start <token>")
    from core.config import ROLE_TOKENS
    role = next((r for r,t in ROLE_TOKENS.items() if t == token), None)
    if not role:
        return await message.reply("Неверный токен")
    await state.update_data(role=role)
    await message.reply(f"Вы зарегистрированы как {role}")
    await show_main_menu(message.chat.id)

# Menu callback handler
@dp.callback_query_handler(menu_cb.filter())
async def handle_menu(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["action"]
    await state.finish()
    user_id = callback.from_user.id
    # Cancel any existing keyboard
    await callback.message.delete()
    if action == MenuActions.NEW:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Отмена", callback_data=cancel_cb.new(action="cancel"))
        )
        await bot.send_message(user_id, "Отправьте URL товара:", reply_markup=kb)
        await NewState.url.set()
    elif action == MenuActions.TRENDS:
        from core.scraper import get_top_trends
        trends = get_top_trends()
        text = "#TOP-10 трендов за 24ч:
" + "
".join(
            f"{i+1}. {p['name']} — {p['orders']} orders" for i,p in enumerate(trends)
        )
        await bot.send_message(user_id, text)
        await show_main_menu(user_id)
    elif action == MenuActions.APPROVE:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Отмена", callback_data=cancel_cb.new(action="cancel"))
        )
        await bot.send_message(user_id, "Укажите ID черновика:", reply_markup=kb)
        await ApproveState.task_id.set()
    elif action == MenuActions.SCHEDULE:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Отмена", callback_data=cancel_cb.new(action="cancel"))
        )
        await bot.send_message(user_id, "Укажите ID и дату (ID DD.MM HH:MM):", reply_markup=kb)
        await ScheduleState.data.set()
    elif action == MenuActions.STATS:
        from core.upload import fetch_stats
        data = fetch_stats()
        text = f"Clicks: {data['clicks']}
CTR: {data['ctr']}%
Sales: {data['sales']}"
        await bot.send_message(user_id, text)
        await show_main_menu(user_id)
    elif action == MenuActions.SETTINGS:
        from handlers.settings import cmd_settings
        await cmd_settings(types.SimpleNamespace(chat=types.SimpleNamespace(id=user_id), reply=bot.send_message), state)
    await callback.answer()

# Cancel handler
@dp.callback_query_handler(cancel_cb.filter())
async def handle_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.delete()
    await show_main_menu(callback.from_user.id)
    await callback.answer("Отменено")

# State handlers
@dp.message_handler(state=NewState.url)
async def process_new(message: types.Message, state: FSMContext):
    url = message.text.strip()
    from workers.tasks import generate_creative
    task = generate_creative.apply_async((url, "RU", ["vk","tiktok","instagram","telegram"]))
    await message.reply(f"Задача создана: ID {task.id}")
    await state.finish()
    await show_main_menu(message.chat.id)

@dp.message_handler(state=ApproveState.task_id)
async def process_approve(message: types.Message, state: FSMContext):
    tid = message.text.strip()
    from core.upload import publish_draft
    try:
        links = publish_draft(tid)
        await message.reply("Опубликовано:
" + "
".join(links))
    except Exception as e:
        await message.reply(str(e))
    await state.finish()
    await show_main_menu(message.chat.id)

@dp.message_handler(state=ScheduleState.data)
async def process_schedule(message: types.Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("Неверный формат. ID DD.MM HH:MM")
    tid, dt = parts[0], parts[1]
    import datetime
    dt_obj = datetime.datetime.strptime(dt, "%d.%m %H:%M")
    from workers.tasks import schedule_publish
    schedule_publish.apply_async((tid, dt_obj.isoformat()))
    await message.reply(f"Запланировано: {tid} на {dt}")
    await state.finish()
    await show_main_menu(message.chat.id)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
```python
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from handlers import start, help, new, trends, approve, schedule, stats, settings
from middlewares.auth import RoleMiddleware

env = os.getenv
BOT_TOKEN = env("BOT_TOKEN")
REDIS_URL = env("REDIS_URL")

storage = RedisStorage2.from_url(REDIS_URL)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

dp.middleware.setup(RoleMiddleware())

# register handlers
start.register(dp)
help.register(dp)
new.register(dp)
trends.register(dp)
approve.register(dp)
schedule.register(dp)
stats.register(dp)
settings.register(dp)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)