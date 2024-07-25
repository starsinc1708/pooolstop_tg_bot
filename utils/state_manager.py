import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.base import StorageKey
import database as db
import os
from dotenv import load_dotenv


load_dotenv()
    
BOT_ID = os.getenv('BOT_ID')

async def set_users_states(dispatcher: Dispatcher):
    logging.info("Setting users states....")
    users = await db.get_all_users()
    for user in users:
        state = await db.get_user_state(user_id=user['user_id'])
        if state:
            storage_key = StorageKey(user_id=user['user_id'], bot_id=int(BOT_ID),
                                     chat_id=user['chat']['id'])
            await dispatcher.storage.set_state(storage_key, state)
