from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from config import ADMIN_IDS


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        user_id = getattr(obj.from_user, "id", None)
        return user_id in ADMIN_IDS