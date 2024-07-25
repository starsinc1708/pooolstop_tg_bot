from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from numpy.f2py.cfuncs import callbacks

from handlers.states import Greeting
from keyboards.Inline_keyboards import (
    main_info_keyboard, back_keyboard, settings_keyboard,
    ratings_keyboard, notifications_keyboard,
    language_keyboard, settings_logout_keyboard, service_keyboard, how_to_earn_more_keyboard
)
from pooolstop_api import tg_api
from utils.locale_parser import get_message_text
import database as db
from utils.logger import handle_update
from utils.notification_sender import configure_rating_message

router = Router()


async def edit_message_and_set_state(callback, state, message_text, reply_markup, new_state, parse_mode="HTML"):
    #db.add_user(callback.from_user, callback.message.chat)
    await callback.message.edit_text(
        text=message_text,
        parse_mode=parse_mode,
        disable_web_page_preview=True,
    )
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await state.set_state(new_state)
    db.set_user_state(callback.from_user.id, state=await state.get_state())
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(F.data.startswith("btn_continue"))
async def send_main_info(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "main_info_linked"),
        main_info_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.main_menu
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_learn_more"))
async def send_contacts(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "learn_more"),
        back_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_how_to_earn_more"))
async def send_contacts(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "how_to_earn_more"),
        how_to_earn_more_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_service"))
async def send_service_info(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "service_msg"),
        service_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_settings"))
async def send_settings(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "settings_msg"),
        settings_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.settings_page
    )


@router.callback_query(StateFilter(Greeting.settings_page), F.data.startswith("settings_logout"))
async def send_after_logout(callback: types.CallbackQuery, state: FSMContext):
    linked = db.check_user_profile_linked(callback.from_user.id)
    if linked:
        message_text = get_message_text(db.get_user_locale(callback.from_user), "successful_logout")
        db.user_desync(callback.from_user.id)
    else:
        message_text = get_message_text(db.get_user_locale(callback.from_user), "no_logout")

    await edit_message_and_set_state(
        callback, state,
        message_text,
        settings_logout_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.settings_page
    )


@router.callback_query(F.data == "main_info_ratings")
async def send_ratings(callback: types.CallbackQuery, state: FSMContext):
    ratings_msg = configure_rating_message(callback.message, callback.from_user.id, db.get_user_locale(callback.from_user), 7, db.get_user_watcher_link(callback.from_user))
    await edit_message_and_set_state(
        callback, state,
        ratings_msg,
        ratings_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.rating_page,
        parse_mode="MARKDOWN"
    )


@router.callback_query(F.data.startswith("main_info_ratings_"))
async def send_ratings_page(callback: types.CallbackQuery):
    period = int(callback.data.split("_")[3]) if len(callback.data.split("_")) == 4 else 7
    ratings_msg = configure_rating_message(callback.message, callback.from_user.id, db.get_user_locale(callback.from_user), period, db.get_user_watcher_link(callback.from_user))

    await callback.message.edit_text(
        text=ratings_msg,
        parse_mode="MARKDOWN",
        disable_web_page_preview=True,
    )
    await callback.message.edit_reply_markup(reply_markup=ratings_keyboard(db.get_user_locale(callback.from_user)))
    db.add_callback_log(callback)
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(StateFilter(Greeting.menu_page, Greeting.rating_page),
                       F.data.startswith("main_info_notifications"))
async def send_notifications(callback: types.CallbackQuery, state: FSMContext):
    notifications_msg = get_message_text(db.get_user_locale(callback.from_user), "do_you_want_sub")
    await edit_message_and_set_state(
        callback, state,
        notifications_msg,
        notifications_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.notifications_ratings_page
    )


@router.callback_query(StateFilter(Greeting.settings_page), F.data.startswith("main_info_language"))
async def send_language_settings(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "main_info_lang_settings"),
        language_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.settings_page
    )


@router.callback_query(F.data.startswith("language_"))
async def accept_language(callback: types.CallbackQuery, state: FSMContext):
    db.set_user_locale(callback.from_user, callback.data.split("_")[1])
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "main_info_linked"),
        main_info_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.main_menu
    )


@router.callback_query(StateFilter(Greeting.notifications_ratings_page), F.data.startswith("subscribe_ratings_notify_period_"))
async def send_after_subscribe(callback: types.CallbackQuery, state: FSMContext):
    sch_period = int(callback.data.split("_")[4])
    db.user_notification_subscribe(
        callback.from_user,
        callback.message.chat,
        "ratings",
        int(callback.data.split("_")[4])
    )
    tg_api.add_scheduler(callback.from_user, callback.message.chat, sch_period)
    # if not db.find_user(callback.from_user.id)['linked']:
    #     db.user_notification_subscribe(
    #         callback.from_user,
    #         callback.message.chat,
    #         "registration_proposal",
    #         int(callback.data.split("_")[4])
    #     )

    successful_sub_msg = get_message_text(db.get_user_locale(callback.from_user), "successful_sub")
    ratings_msg = configure_rating_message(callback.message, callback.from_user.id, db.get_user_locale(callback.from_user), 7, db.get_user_watcher_link(callback.from_user))

    await callback.message.edit_text(
        text=successful_sub_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.message.answer(
        ratings_msg,
        parse_mode="MARKDOWN",
        disable_web_page_preview=True,
        reply_markup=ratings_keyboard(db.get_user_locale(callback.from_user))
    )
    await state.set_state(Greeting.rating_page)
    db.set_user_state(callback.from_user.id, state=await state.get_state())
    db.add_callback_log(callback)
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(StateFilter(Greeting.notifications_ratings_page), F.data.startswith("unsubscribe_ratings"))
async def send_after_unsubscribe(callback: types.CallbackQuery, state: FSMContext):
    db.user_notification_unsubscribe(
        callback.from_user,
        "ratings",
    )
    tg_api.delete_scheduler(callback.from_user, callback.message.chat)
    successful_unsub_msg = get_message_text(db.get_user_locale(callback.from_user), "successful_unsub")

    await callback.message.edit_text(
        text=successful_unsub_msg,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.message.answer(
        get_message_text(db.get_user_locale(callback.from_user), "main_info_linked"),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=main_info_keyboard(db.get_user_locale(callback.from_user))
    )
    await state.set_state(Greeting.main_menu)
    db.set_user_state(callback.from_user.id, state=await state.get_state())
    db.add_callback_log(callback)
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(F.data.startswith("main_info_back"))
async def send_main_info_after_back_btn(callback: types.CallbackQuery, state: FSMContext):
    await edit_message_and_set_state(
        callback, state,
        get_message_text(db.get_user_locale(callback.from_user), "main_info_linked"),
        main_info_keyboard(db.get_user_locale(callback.from_user)),
        Greeting.main_menu
    )
