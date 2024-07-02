import logging
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from services.database import get_user_role, get_admin_count, get_user_path


# Проверка уровня доступа к системе.
class UserData(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        admin_count = await get_admin_count()
        role_id = await get_user_role(user_id=user.id) if admin_count > 0 else 2
        data["role_id"] = role_id
        user_path = await get_user_path(user_id=user.id)
        data["path"] = user_path
        logging.log(
            msg=f'Message from {user.id} ({user.full_name}), level: {role_id}, path: {user_path}',
            level=logging.INFO)
        return await handler(event, data)
