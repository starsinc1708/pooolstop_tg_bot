import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
import aiohttp_cors
from handlers import callbacks, global_commands, text_messages, http_handler
from utils.notification_sender import send_rating_notification
from utils.state_manager import set_users_states
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings()

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


async def main_bot():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(global_commands.router)
    dp.include_router(text_messages.router)
    dp.include_router(callbacks.router)

    #scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    #scheduler.add_job(send_rating_notification, trigger='interval', minutes=1, kwargs={'bot': bot, 'dispatcher': dp})
    #scheduler.start()

    await asyncio.create_task(set_users_states(dp))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main_server():
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={"*": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*")})
    http_handler.setup_routes(app)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8084)
    await site.start()


async def main():
    await asyncio.gather(main_bot(), main_server())

if __name__ == "__main__":
    asyncio.run(main())

