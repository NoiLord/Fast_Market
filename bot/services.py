"""Вспомогательные сервисные функции."""
from aiogram import Bot
from config import ADMIN_IDS


async def notify_admins(bot: Bot, text: str, reply_markup=None) -> None:
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, reply_markup=reply_markup)
        except Exception:
            pass