from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from workers.tasks import publish_task
from datetime import datetime, timedelta
from workers.tasks import schedule_publish
from bot.handlers.trends import cmd_trends
from bot.handlers.stats import cmd_stats
from bot.handlers.settings import cmd_settings


async def on_approve(callback: types.CallbackQuery):
    draft_id = callback.data.split(":", 1)[1]
    res = publish_task.delay(draft_id)
    await callback.message.answer(f"🚀 Публикация черновика {draft_id} запущена. Задача: {res.id}")
    await callback.answer()


async def on_schedule(callback: types.CallbackQuery):
    draft_id = callback.data.split(":", 1)[1]
    # Предложим быстрый выбор времени
    kb = InlineKeyboardMarkup(row_width=3)
    for label, offset in [("▶️ Сейчас", 0), ("⏱️ +1ч", 1), ("⏱️ +3ч", 3)]:
        kb.insert(InlineKeyboardButton(label, callback_data=f"sched:{draft_id}:{offset}"))
    kb.add(InlineKeyboardButton("🏠 Меню", callback_data="menu:home"))
    await callback.message.answer("Выберите время публикации:", reply_markup=kb)
    await callback.answer()


async def on_sched(callback: types.CallbackQuery):
    _, draft_id, offset_str = callback.data.split(":", 2)
    offset = int(offset_str)
    if offset == 0:
        res = publish_task.delay(draft_id)
        await callback.message.answer(f"🚀 Публикация черновика {draft_id} запущена. Задача: {res.id}")
    else:
        eta = (datetime.utcnow() + timedelta(hours=offset)).replace(second=0, microsecond=0)
        schedule_publish.delay(draft_id, eta.isoformat())
        await callback.message.answer(f"🗓️ Публикация {draft_id} запланирована через {offset} ч.")
    await callback.answer()


async def on_menu(callback: types.CallbackQuery):
    _, action = callback.data.split(":", 1)
    if action == "home":
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🎬 Создать черновик", callback_data="menu:new"),
            InlineKeyboardButton("🔥 Тренды", callback_data="menu:trends"),
            InlineKeyboardButton("📊 Статистика", callback_data="menu:stats"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="menu:settings"),
        )
        await callback.message.answer("🏠 Главное меню", reply_markup=kb)
    elif action == "new":
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("🏠 Меню", callback_data="menu:home"))
        await callback.message.answer("Вставьте ссылку на товар и отправьте команду: /new <URL>", reply_markup=kb)
    elif action == "trends":
        await cmd_trends(callback.message)
    elif action == "stats":
        await cmd_stats(callback.message)
    elif action == "settings":
        await cmd_settings(callback.message)
    await callback.answer()


def register(dp: Dispatcher):
    dp.register_callback_query_handler(on_approve, lambda cb: cb.data.startswith("approve:"))
    dp.register_callback_query_handler(on_schedule, lambda cb: cb.data.startswith("schedule:"))
    dp.register_callback_query_handler(on_sched, lambda cb: cb.data.startswith("sched:"))
    dp.register_callback_query_handler(on_menu, lambda cb: cb.data.startswith("menu:"))

