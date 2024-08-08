from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import database as db
from handlers.states import Greeting
from keyboards.Inline_keyboards import main_info_keyboard, main_info_keyboard_admin
from utils.locale_parser import get_message_text
from utils.logger import handle_update
import os
from dotenv import load_dotenv
from pooolstop_api import tg_api

load_dotenv()
    
BOT_TOKEN = os.getenv('BOT_TOKEN')



bot = Bot(token=BOT_TOKEN)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    command_parts = message.text.split()
    source = command_parts[1] if len(command_parts) > 1 else 'telegram'
    exists = await db.find_user(message.from_user.id)
    if not exists:
        await db.add_user(message.from_user, message.chat)
        tg_api.add_user(message.from_user, message.chat)
        await db.save_user_ad_source(message.from_user, source)

    is_admin = await db.is_user_admin(message.from_user)
    locale = await db.get_user_locale(message.from_user)
    await message.answer(
        get_message_text(locale, "main_info_linked"),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=main_info_keyboard_admin(locale) if is_admin else main_info_keyboard(locale),
    )

    await state.set_state(Greeting.main_menu)

    await db.add_command_log(message)
    await db.set_user_state(user_id=message.from_user.id, state=await state.get_state())
    await handle_update(message=message)


# @router.message(Command("menu"))
# async def cmd_menu(message: Message, state: FSMContext):
#     await remove_keyboard(message)
#     linked = db.check_user_profile_linked(message.from_user.id)
#     if linked:
#         await message.answer(
#             get_message_text(db.get_user_locale(message.from_user), "main_info_linked"),
#             parse_mode="HTML",
#             disable_web_page_preview=True,
#             reply_markup=main_info_keyboard(db.get_user_locale(message.from_user))
#         )
#     else:
#         await message.answer(
#             get_message_text(db.get_user_locale(message.from_user), "main_info_not_linked"),
#             parse_mode="HTML",
#             disable_web_page_preview=True,
#             reply_markup=main_info_keyboard(db.get_user_locale(message.from_user))
#         )
#     await state.set_state(Greeting.main_menu)
#     db.add_command_log(message)
#     db.set_user_state(user_id=message.from_user.id, state=await state.get_state())
#     await handle_update(message=message)
#
#
# @router.message(Command("settings"))
# async def cmd_settings(message: Message, state: FSMContext):
#     await remove_keyboard(message)
#     setting_msg = get_message_text(db.get_user_locale(message.from_user), "settings_msg")
#     await message.answer(
#         setting_msg,
#         parse_mode="HTML",
#         disable_web_page_preview=True,
#         reply_markup=settings_keyboard(db.get_user_locale(message.from_user))
#     )
#     await state.set_state(Greeting.settings_page)
#     db.add_command_log(message)
#     db.set_user_state(user_id=message.from_user.id, state=await state.get_state())
#    await handle_update(message=message)


# @router.message(Command("ratings"))
# async def cmd_ratings(message: Message, state: FSMContext):
#     await remove_keyboard(message)
#     period = 7
#     ratings_msg = configure_rating_message(db.get_user_locale(message.from_user), period)
#     await message.answer(
#         text=ratings_msg,
#         parse_mode="HTML",
#         disable_web_page_preview=True,
#         reply_markup=ratings_keyboard(db.get_user_locale(message.from_user))
#     )
#     await state.set_state(Greeting.rating_page)
#     db.add_command_log(message)
#     db.set_user_state(user_id=message.from_user.id, state=await state.get_state())
#     await handle_update(message=message)
#
#
# @router.message(Command("profile"))
# async def cmd_profile(message: Message, state: FSMContext):
#     await remove_keyboard(message)
#     linked = db.check_user_profile_linked(message.from_user.id)
#     if linked:
#         user_info_msg = await db.get_user_info(db.get_user_locale(message.from_user), message.from_user.id)
#         await message.answer(
#             text=user_info_msg,
#             parse_mode="HTML",
#             disable_web_page_preview=True,
#             reply_markup=linked_profile_keyboard(db.get_user_locale(message.from_user))
#         )
#         await state.set_state(Greeting.profile_page)
#         db.set_user_state(message.from_user.id, state=await state.get_state())
#     else:
#         await message.answer(
#             text=get_message_text(db.get_user_locale(message.from_user), "not_linked_profile"),
#             parse_mode="HTML",
#             disable_web_page_preview=True,
#             reply_markup=account_doesnt_connected(db.get_user_locale(message.from_user))
#         )
