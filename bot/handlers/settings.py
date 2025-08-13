from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


LANGS = ["RU", "UZ", "KZ", "EN"]
PLATFORMS = ["vk", "tiktok", "instagram", "telegram"]


class SettingsState(StatesGroup):
    choosing = State()


async def cmd_settings(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    for lang in LANGS:
        kb.insert(InlineKeyboardButton(text=lang, callback_data=f"lang:{lang}"))
    for p in PLATFORMS:
        kb.insert(InlineKeyboardButton(text=p.title(), callback_data=f"plat:{p}"))
    await message.reply(
        "Выберите языки и платформы (повторно нажмите для переключения). Когда закончили, введите /done",
        reply_markup=kb,
    )
    await SettingsState.choosing.set()


async def cb_choice(callback: types.CallbackQuery, state: FSMContext):
    key, value = callback.data.split(":", 1)
    data = await state.get_data()
    current = set(data.get(key, []))
    if value in current:
        current.remove(value)
        action = "удалён"
    else:
        current.add(value)
        action = "добавлен"
    data[key] = list(current)
    await state.update_data(**data)
    await callback.answer(f"{value} {action}")


async def cmd_settings_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    langs = data.get("lang", [])
    plats = data.get("plat", [])
    await message.reply(
        f"Настройки сохранены.\nЯзыки: {', '.join(langs)}\nПлатформы: {', '.join(plats)}"
    )
    await state.finish()


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_settings, commands=["settings"], state="*")
    dp.register_callback_query_handler(cb_choice, lambda c: ":" in c.data, state=SettingsState.choosing)
    dp.register_message_handler(cmd_settings_done, commands=["done"], state=SettingsState.choosing)

