import logging
from aiogram import types
from aiogram.types import Message
import database as db


async def handle_update(message: Message = None, callback: types.CallbackQuery = None):
    if message is not None:
        logging.info(
            f"Received message '{message.text}' from chat id={message.chat.id}, user id={message.from_user.id}, username={message.from_user.username}")
        db.add_message_log(message)
    elif callback is not None:
        logging.info(
            f"Received callback data '{callback.data}' from chat id={callback.message.chat.id}, user id={callback.from_user.id}, username={callback.from_user.username}")
        db.add_callback_log(callback)