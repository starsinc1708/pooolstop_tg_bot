from aiogram import types
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.locale_parser import get_btn_text
import os
from dotenv import load_dotenv

load_dotenv()

URL_BASE = os.getenv('WEBAPP_URL_BASE')
ABOUT_US_URL = os.getenv('ABOUT_US_URL')
QUESTION_BOT_URL = os.getenv('QUESTION_BOT_URL')


def get_inline_keyboard(message_type, locale="en"):
    if message_type == 'rating_notify':
        return ratings_keyboard(locale)
    elif message_type == 'back':
        return back_keyboard(locale)
    elif message_type == 'bot_update':
        return bot_update_keyboard(locale)
    else:
        return back_keyboard(locale)


def main_info_keyboard_admin(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_learn_more'),
            callback_data="main_info_learn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_ratings'),
            callback_data="main_info_ratings"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_how_to_earn_more'),
            callback_data="main_info_how_to_earn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_profile'),
            web_app=WebAppInfo(url=URL_BASE)
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_service'),
            callback_data="main_info_service"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_settings'),
            callback_data="main_info_settings"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_admin'),
            callback_data="main_info_open_admin_panel"
        ),
    )
    return kb.as_markup(resize_keyboard=True)

def admin_panel_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_new_user_stat'),
            callback_data="admin_new_users_stat"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back_admin'),
            callback_data="admin_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)



def main_info_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_learn_more'),
            callback_data="main_info_learn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_ratings'),
            callback_data="main_info_ratings"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_how_to_earn_more'),
            callback_data="main_info_how_to_earn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_profile'),
            web_app=WebAppInfo(url=URL_BASE)
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_service'),
            callback_data="main_info_service"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_settings'),
            callback_data="main_info_settings"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def back_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def how_to_earn_more_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_profile'),
            web_app=WebAppInfo(url=URL_BASE)
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def to_menu_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_to_menu'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def registration_proposal_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_register_in_webapp'),
            web_app=WebAppInfo(url=URL_BASE)
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_to_menu'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def service_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_call_manager'),
            url=QUESTION_BOT_URL
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_question'),
            url=QUESTION_BOT_URL
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def settings_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_language'),
            callback_data="main_info_language"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def bot_update_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_learn_more'),
            callback_data="main_info_learn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_how_to_earn_more'),
            callback_data="main_info_how_to_earn_more"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_to_menu'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def settings_logout_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def new_user_stat_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_1'),
            callback_data="new_user_stat_1"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_7'),
            callback_data="new_user_stat_7"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_30'),
            callback_data="new_user_stat_30"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back_to_admin'),
            callback_data="back_to_admin"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def ratings_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_7'),
            callback_data="main_info_ratings_7"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_30'),
            callback_data="main_info_ratings_30"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_90'),
            callback_data="main_info_ratings_90"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_180'),
            callback_data="main_info_ratings_180"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_365'),
            callback_data="main_info_ratings_365"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_notifications'),
            callback_data="main_info_notifications"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def notifications_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_1'),
            callback_data="subscribe_ratings_notify_period_1"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_7'),
            callback_data="subscribe_ratings_notify_period_7"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_period_30'),
            callback_data="subscribe_ratings_notify_period_30"
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_unsubscribe'),
            callback_data="unsubscribe_ratings"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def linked_profile_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_webapp_open'),
            web_app=WebAppInfo(url=URL_BASE)
        ),
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_statistics'),
            callback_data="profile_statistics"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_workers'),
            callback_data="profile_workers"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_wallet'),
            callback_data="profile_wallet"
        )
    )
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_back'),
            callback_data="main_info_back"
        ),
    )
    return kb.as_markup(resize_keyboard=True)


def language_keyboard(locale: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_en'),
            callback_data="language_en"
        ),
        types.InlineKeyboardButton(
            text=get_btn_text(locale, 'btn_ru'),
            callback_data="language_ru"
        )
    )
    return kb.as_markup(resize_keyboard=True)
