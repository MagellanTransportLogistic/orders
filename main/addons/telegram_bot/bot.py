import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from magellan_web.settings import BOT_TOKEN, DATABASES as db
from main.addons.telegram_bot.handlers import common, register_user, remove_user, change_user, send_doc
from main.addons.telegram_bot.middlewares.access import UserData
from main.addons.telegram_bot.services.database import sql_start


# from main.addons.telegram_bot.services.database import sql_start


def create_pool():
    sql_start(db['default']['NAME'], db['default']['HOST'], db['default']['USER'],
              db['default']['PASSWORD'])


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    bot = Bot(BOT_TOKEN)
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
