from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from core.config import ROLE_TOKENS

async def cmd_start(message: types.Message, state: FSMContext):
    token = message.get_args().strip()
    if not token:
        return await message.reply(
            "Добро пожаловать! Чтобы зарегистрироваться, используйте /start <token>"
        )
    role = next((r for r, t in ROLE_TOKENS.items() if t == token), None)
    if not role:
        return await message.reply("Неверный токен. Повторите ввод.")
    # Сохранение роли в состоянии пользователя
    await state.update_data(role=role)
    await message.reply(f"Вы успешно зарегистрированы как {role}.")


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
```python
from aiogram import types, Dispatcher

async def cmd_start(message: types.Message):
    # register user and assign role
    await message.reply("Добро пожаловать! Используйте /help для списка команд.")


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])