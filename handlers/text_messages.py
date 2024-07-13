from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pyexpat.errors import messages

import database as db
from handlers.states import Greeting
from keyboards.Inline_keyboards import main_info_keyboard, continue_keyboard, ratings_keyboard, back_keyboard
from utils.locale_parser import get_message_text
from utils.logger import handle_update
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
router = Router()


async def edit_message_and_set_state(message: Message, state, message_text, reply_markup, new_state):
    await message.answer(
        text=message_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    await state.set_state(new_state)
    db.set_user_state(message.from_user.id, state=await state.get_state())
    await handle_update(message=message)


@router.message(F.text, StateFilter(Greeting.rating_page))
async def watcher_link(message: Message, state: FSMContext):
    from utils.notification_sender import configure_rating_message_with_watcher
    ratings_msg = configure_rating_message_with_watcher(message.text, db.get_user_locale(message.from_user), 7)
    await edit_message_and_set_state(
        message, state,
        ratings_msg,
        back_keyboard(db.get_user_locale(message.from_user)),
        Greeting.rating_page
    )

