from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
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
    await db.add_user(callback.from_user, callback.message.chat)
    await callback.message.edit_text(
        text=message_text,
        parse_mode=parse_mode,
        disable_web_page_preview=True,
    )
    await callback.message.edit_reply_markup(reply_markup=reply_markup)
    await state.set_state(new_state)
    await db.set_user_state(callback.from_user.id, state=await state.get_state())
    await callback.answer()
    await handle_update(callback=callback)




@router.callback_query(F.data.startswith("btn_continue"))
async def send_main_info(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "main_info_linked"),
        main_info_keyboard(locale),
        Greeting.main_menu
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_learn_more"))
async def send_contacts(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "learn_more"),
        back_keyboard(locale),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_how_to_earn_more"))
async def send_contacts(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "how_to_earn_more"),
        how_to_earn_more_keyboard(locale),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_service"))
async def send_service_info(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "service_msg"),
        service_keyboard(locale),
        Greeting.menu_page
    )


@router.callback_query(StateFilter(Greeting.main_menu), F.data.startswith("main_info_settings"))
async def send_settings(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "settings_msg"),
        settings_keyboard(locale),
        Greeting.settings_page
    )


@router.callback_query(StateFilter(Greeting.settings_page), F.data.startswith("settings_logout"))
async def send_after_logout(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    linked = await db.check_user_profile_linked(callback.from_user.id)  
    if linked:
        message_text = get_message_text(locale, "successful_logout")
        await db.user_desync(callback.from_user.id)  
    else:
        message_text = get_message_text(locale, "no_logout")

    await edit_message_and_set_state(
        callback, state,
        message_text,
        settings_logout_keyboard(locale),
        Greeting.settings_page
    )


@router.callback_query(F.data == "main_info_ratings")
async def send_ratings(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    watcher_link = await db.get_user_watcher_link(callback.from_user)  
    ratings_msg = await configure_rating_message(callback.message, callback.from_user.id, locale, 7, watcher_link)
    await edit_message_and_set_state(
        callback, state,
        ratings_msg,
        ratings_keyboard(locale),
        Greeting.rating_page,
        parse_mode="MARKDOWN"
    )


@router.callback_query(F.data.startswith("main_info_ratings_"))
async def send_ratings_page(callback: types.CallbackQuery):
    period = int(callback.data.split("_")[3]) if len(callback.data.split("_")) == 4 else 7
    locale = await db.get_user_locale(callback.from_user)
    watcher_link = await db.get_user_watcher_link(callback.from_user)
    ratings_msg = await configure_rating_message(callback.message, callback.from_user.id, locale, period, watcher_link)

    await callback.message.edit_text(
        text=ratings_msg,
        parse_mode="MARKDOWN",
        disable_web_page_preview=True,
    )
    await callback.message.edit_reply_markup(reply_markup=ratings_keyboard(locale))
    await db.add_callback_log(callback)
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(StateFilter(Greeting.menu_page, Greeting.rating_page),
                       F.data.startswith("main_info_notifications"))
async def send_notifications(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    notifications_msg = get_message_text(locale, "do_you_want_sub")
    await edit_message_and_set_state(
        callback, state,
        notifications_msg,
        notifications_keyboard(locale),
        Greeting.notifications_ratings_page
    )


@router.callback_query(StateFilter(Greeting.settings_page), F.data.startswith("main_info_language"))
async def send_language_settings(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "main_info_lang_settings"),
        language_keyboard(locale),
        Greeting.settings_page
    )


@router.callback_query(F.data.startswith("language_"))
async def accept_language(callback: types.CallbackQuery, state: FSMContext):
    await db.set_user_locale(callback.from_user, callback.data.split("_")[1])  
    locale = await db.get_user_locale(callback.from_user)  
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "main_info_linked"),
        main_info_keyboard(locale),
        Greeting.main_menu
    )


@router.callback_query(StateFilter(Greeting.notifications_ratings_page), F.data.startswith("subscribe_ratings_notify_period_"))
async def send_after_subscribe(callback: types.CallbackQuery, state: FSMContext):
    sch_period = int(callback.data.split("_")[4])
    await db.user_notification_subscribe(
        callback.from_user,
        callback.message.chat,
        "ratings",
        sch_period
    )  
    tg_api.add_scheduler(callback.from_user, callback.message.chat, sch_period)
    locale = await db.get_user_locale(callback.from_user)  
    ratings_msg = await configure_rating_message(callback.message, callback.from_user.id, locale, 7,
                                           await db.get_user_watcher_link(callback.from_user))  

    await callback.message.edit_text(
        text=get_message_text(locale, "successful_sub"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.message.answer(
        ratings_msg,
        parse_mode="MARKDOWN",
        disable_web_page_preview=True,
        reply_markup=ratings_keyboard(locale)
    )
    await state.set_state(Greeting.rating_page)
    await db.set_user_state(callback.from_user.id, state=await state.get_state())
    await db.add_callback_log(callback)
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(StateFilter(Greeting.notifications_ratings_page), F.data.startswith("unsubscribe_ratings"))
async def send_after_unsubscribe(callback: types.CallbackQuery, state: FSMContext):
    await db.user_notification_unsubscribe(
        callback.from_user,
        "ratings",
    )  
    tg_api.delete_scheduler(callback.from_user, callback.message.chat)
    locale = await db.get_user_locale(callback.from_user)  

    await callback.message.edit_text(
        text=get_message_text(locale, "successful_unsub"),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await callback.message.answer(
        get_message_text(locale, "main_info_linked"),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=main_info_keyboard(locale)
    )
    await state.set_state(Greeting.main_menu)
    await db.set_user_state(callback.from_user.id, state=await state.get_state())  
    await db.add_callback_log(callback)  
    await callback.answer()
    await handle_update(callback=callback)


@router.callback_query(F.data.startswith("main_info_back"))
async def send_main_info_after_back_btn(callback: types.CallbackQuery, state: FSMContext):
    locale = await db.get_user_locale(callback.from_user)  
    await edit_message_and_set_state(
        callback, state,
        get_message_text(locale, "main_info_linked"),
        main_info_keyboard(locale),
        Greeting.main_menu
    )
