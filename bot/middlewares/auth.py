from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
import os


class RoleMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int):
        super().__init__()
        self.admin_id = int(admin_id)

    async def on_pre_process_message(self, message, data):
        user_id = getattr(message.from_user, "id", None)
        if user_id != self.admin_id:
            try:
                await message.reply("Доступ запрещён. Обратитесь к администратору.")
            except Exception:
                pass
            raise CancelHandler()
        data["role"] = "Admin"

    async def on_pre_process_callback_query(self, callback, data):
        user_id = getattr(callback.from_user, "id", None)
        if user_id != self.admin_id:
            try:
                await callback.answer("Доступ запрещён", show_alert=True)
            except Exception:
                pass
            raise CancelHandler()
        data["role"] = "Admin"

