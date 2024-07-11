import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import callbacks, global_commands
from utils.notification_sender import send_rating_notification
from utils.state_manager import set_users_states
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings()

async def main():
    logging.basicConfig(level=logging.INFO)

    load_dotenv()
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(global_commands.router)
    dp.include_router(callbacks.router)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_rating_notification, trigger='interval', minutes=30, kwargs={'bot': bot, 'dispatcher': dp})
    scheduler.start()

    await asyncio.create_task(set_users_states(dp))

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
