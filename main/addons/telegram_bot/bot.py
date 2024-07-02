import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv
from handlers import common, register_user, remove_user, change_user, send_doc
from middlewares.access import UserData
from services.database import sql_start


def read_settings(param_name: str):
    def get_variable(name: str, default_value: bool | None = None) -> str | None | bool:
        true_ = ('true', '1', 't', 'yes')
        false_ = ('false', '0', 'f', 'no')
        value: str | None = os.getenv(name, None)
        if value is None:
            if default_value is None:
                raise ValueError(f'Variable `{name}` not set!')
            else:
                value = str(default_value)
        if value.lower() not in true_ + false_:
            return value
        return value.lower() in true_

    load_dotenv('.env')
    return get_variable(param_name)


def create_pool():
    db_name = read_settings('SQL_DB_NAME')
    db_host = read_settings('SQL_DB_HOST')
    db_user = read_settings('SQL_DB_USER')
    db_pasw = read_settings('SQL_DB_PASSWORD')

    sql_start(db_name, db_host, db_user, db_pasw)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(read_settings('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(UserData())

    dp.include_router(common.router_common)
    dp.include_router(register_user.router_register_user)
    dp.include_router(change_user.router_change_user)
    dp.include_router(remove_user.router_remove_user)
    dp.include_router(send_doc.router_send_doc)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, on_startup=create_pool())


def load():
    print(f'Loaded telegram bot.' + chr(13) + chr(10))
    asyncio.run(main())


if __name__ == '__main__':
    asyncio.run(main())
