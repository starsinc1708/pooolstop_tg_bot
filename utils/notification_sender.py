import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey
from handlers.states import Greeting
from keyboards.Inline_keyboards import registration_proposal_keyboard
import database as db
from utils.locale_parser import get_message_text
from pooolstop_api import rating_service as rs
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv('BOT_ID')

def format_pool_row(pool, with_user=False):
    rating = f"{pool['rating']}"
    payrate = f"{pool['payrate']:<4.2f}"
    percent = f"{pool['percent']:<6.2f}"
    if with_user and pool['is_user']:
        name = f"[YOU]"
        return f"*{rating})  {name} - {payrate} | {percent}%*\n"
    else:
        name = f"[{pool['pool']}]({pool['pool_url']})"
        return f"{rating})  {name} - {payrate} | {percent}%\n"

def configure_message_head_and_footer(locale, head_key, footer_key, period=None):
    msg = get_message_text(locale, head_key)
    if period:
        msg = msg.format(period)
    msg += get_message_text(locale, footer_key)
    return msg

def configure_rating_message(locale, period, watcher_link=None):
    head_key = "ratings_msg_head_watcher" if watcher_link else "ratings_msg_head"
    footer_key = "ratings_msg_footer_watcher" if watcher_link else "ratings_msg_footer"
    msg = ""
    pools = rs.get_ratings_for_table_with_watcher(watcher_link, period) if watcher_link else rs.get_ratings_for_table(period)
    for pool in pools:
        msg += format_pool_row(pool, with_user=watcher_link is not None)
    msg += configure_message_head_and_footer(locale, head_key, footer_key, period)
    return msg

def configure_rating_notification(locale, period):
    msg = ""
    pools = rs.get_ratings_for_table(period)
    for pool in pools:
        msg += get_message_text(locale, "ratings_pool_row").format(pool['rating'], pool['pool_url'], pool['pool'], pool['payrate'], pool['percent'])
    msg += configure_message_head_and_footer(locale, "ratings_notification_head", "ratings_msg_footer", period)
    return msg

def configure_registration_proposal(locale):
    return get_message_text(locale, "you_can_register")

async def send_notifications(bot, dispatcher, notification_type, configure_msg_func, target_state, keyboard_func=None):
    notifications = []
    for item in db.notifications.find({'notification_type': notification_type}):
        last_notification = datetime.fromisoformat(str(item['last_notification_datetime']))
        period = item['period']
        if last_notification <= datetime.utcnow() - timedelta(days=period):
            user = db.find_user(item['user_id'])
            notification = {
                'user_id': item['user_id'],
                'chat_id': item['chat']['id'],
                'msg': configure_msg_func(user['locale'], period),
                'locale': user['locale']
            }
            notifications.append(notification)

    logging.info(f"Started sending notifications[{notification_type}]... {len(notifications)}")

    for notification in notifications:
        try:
            await bot.send_message(notification['chat_id'], notification['msg'],
                                   parse_mode="HTML",
                                   disable_web_page_preview=True,
                                   reply_markup=keyboard_func(notification['locale']) if keyboard_func else None)

            db.update_notification(notification['user_id'], notification_type)
            db.set_user_state(notification['user_id'], state=target_state.state)

            state = db.get_user_state(user_id=notification['user_id'])
            storage_key = StorageKey(user_id=notification['user_id'], bot_id=int(BOT_ID), chat_id=notification['chat_id'])
            await dispatcher.storage.set_state(storage_key, state)

        except Exception as e:
            logging.error(f"Failed to send notification to {notification['user_id']}: {e}")

async def send_registration_proposal(bot: Bot, dispatcher: Dispatcher):
    await send_notifications(bot, dispatcher, "registration_proposal", configure_registration_proposal, Greeting.menu_page, registration_proposal_keyboard)

async def send_rating_notification(bot: Bot, dispatcher: Dispatcher):
    await send_notifications(bot, dispatcher, "ratings", configure_rating_notification, Greeting.rating_page)
    await send_registration_proposal(bot, dispatcher)
