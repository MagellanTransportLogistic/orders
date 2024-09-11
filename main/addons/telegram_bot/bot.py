import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv
from handlers import common, register_user, remove_user, change_user, send_doc
from middlewares.access import UserData
from services.database import sql_start, get_group_messages, erase_group_message


async def check_group_messages(bot: Bot):
    buffer = get_group_messages()
    for k in buffer:
        await asyncio.sleep(0.5)
        # Не будет останавливаться на одном некорректном сообщении. Но оно будет оставаться в буфере не отправленных.
        try:
            result = await bot.send_message(chat_id=k[0], text=k[1], parse_mode='HTML')
            if isinstance(result, Message):
                erase_group_message(k[2])
        except Exception as e:
            logging.critical(f'Error in message uuid: {str(k[2])}: {str(e)}')


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


async def main():
    def on_start():
        db_name = read_settings('SQL_DB_NAME')
        db_host = read_settings('SQL_DB_HOST')
        db_user = read_settings('SQL_DB_USER')
        db_pasw = read_settings('SQL_DB_PASSWORD')
        db_options = read_settings('SQL_OPTIONS')
        sql_start(db_name, db_host, db_user, db_pasw, db_options)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(read_settings('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())
    scheduler = AsyncIOScheduler()
    dp.update.outer_middleware(UserData())

    dp.include_router(common.router_common)
    dp.include_router(register_user.router_register_user)
    dp.include_router(change_user.router_change_user)
    dp.include_router(remove_user.router_remove_user)
    dp.include_router(send_doc.router_send_doc)

    scheduler.add_job(check_group_messages, 'interval', seconds=5, args=[bot])

    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, on_startup=on_start())


def load():
    print(f'Loaded telegram bot.' + chr(13) + chr(10))
    asyncio.run(main())


if __name__ == '__main__':
    asyncio.run(main())
