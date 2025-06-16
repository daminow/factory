from aiogram import types, Dispatcher

async def cmd_help(message: types.Message):
    text = (
        "/start - приветствие\n"
        "/help - справочник команд\n"
        "/new <URL> - создать черновик видео\n"
        "/trends - топ-10 товаров за 24ч\n"
        "/approve <ID> - опубликовать черновик\n"
        "/schedule <ID> DD.MM HH:MM - отложить публикацию\n"
        "/stats - статистика кликов и продаж\n"
        "/settings - настройки платформ и языков\n"
        "/ai - текущее расходование API"
    )
    await message.reply(text)


def register(dp: Dispatcher):
    dp.register_message_handler(cmd_help, commands=["help"])