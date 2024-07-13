import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey
from sympy.physics.units import percent

from handlers.states import Greeting
from handlers.text_messages import watcher_link
from keyboards.Inline_keyboards import ratings_keyboard, back_keyboard, to_menu_keyboard, registration_proposal_keyboard
import database as db
from utils.locale_parser import get_message_text
from pooolstop_api import rating_service as rs
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv('BOT_ID')


def configure_rating_message(locale: str, period: int) -> str:
    msg = get_message_text(locale, "ratings_msg_head").format(period)
    pools = rs.get_ratings_for_table(period)
    header = "`Rating | Pool Name                | Payrate | Percent `\n"
    separator = "`------ | ------------------------ | ------- | ------- `\n"
    msg += header + separator

    for pool in pools:
        rating = f"{pool['rating']:<6}"
        name = f"{pool['pool']:<24}"
        payrate = f"{pool['payrate']:<7.2f}"
        percent = f"{pool['percent']:<6.2f}"
        msg += f"`{rating} | {name} | {payrate} | {percent} %`\n"

    msg += get_message_text(locale, "ratings_msg_footer")
    return msg


def configure_rating_message_with_watcher(link: str, locale: str, period: int) -> str:
    msg = get_message_text(locale, "ratings_msg_head").format(period)
    pools = rs.get_ratings_for_table_with_watcher(link, period)
    header = "`Rating | Pool Name                | Payrate | Percent `\n"
    separator = "`------ | ------------------------ | ------- | ------- `\n"
    msg += header + separator

    # for pool in pools:
    #     if pool['is_user']:
    #         watcher = "*YOU*"
    #         name = f"{watcher:<24}"
    #     else:
    #         name = f"{pool['pool']:<24}"
    #
    #     rating = f"{pool['rating']:<6}"
    #     payrate = f"{pool['payrate']:<7.2f}"
    #     percent = f"{pool['percent']:<6.2f}"
    #     msg += f"`{rating} | {name} | {payrate} | {percent} %`\n"
    #
    # msg += get_message_text(locale, "ratings_msg_footer")
    return msg


def configure_rating_notification(locale: str, period: int) -> str:
    msg = get_message_text(locale, "ratings_notification_head")
    msg += get_message_text(locale, "ratings_msg_head").format(period)
    pools = rs.get_ratings_for_table(period)
    for pool in pools:
        msg += get_message_text(locale, "ratings_pool_row").format(pool['rating'], pool['pool_url'], pool['pool'],
                                                                   pool['payrate'], pool['percent'])
    return msg


def configure_registration_proposal(locale: str, period: int) -> str:
    msg = get_message_text(locale, "you_can_register")
    return msg


async def send_registration_proposal(bot: Bot, dispatcher: Dispatcher):
    notifications = []
    for item in db.notifications.find({'notification_type': "registration_proposal"}):
        last_notification = datetime.fromisoformat(str(item['last_notification_datetime']))
        period = item['period']
        if last_notification <= datetime.utcnow() - timedelta(days=period):
            notification = {
                'user_id': item['user_id'],
                'chat_id': item['chat']['id'],
                'msg': configure_registration_proposal(db.find_user(item['user_id'])['locale'], 7),
                'locale': db.find_user(item['user_id'])['locale']
            }
            notifications.append(notification)

    logging.info(f"Started sending notifications[registration_proposal]... {len(notifications)}")

    for notification in notifications:
        try:
            await bot.send_message(notification['chat_id'], notification['msg'],
                                   parse_mode="HTML",
                                   disable_web_page_preview=True,
                                   reply_markup=registration_proposal_keyboard(notification['locale']))

            db.update_notification(notification['user_id'], "registration_proposal")
            db.set_user_state(notification['user_id'], state=Greeting.menu_page.state)

            state = db.get_user_state(user_id=notification['user_id'])
            storage_key = StorageKey(user_id=notification['user_id'], bot_id=int(BOT_ID),
                                     chat_id=notification['chat_id'])
            await dispatcher.storage.set_state(storage_key, state)

        except Exception as e:
            logging.error(f"Failed to send notification to {notification['user_id']}: {e}")


async def send_rating_notification(bot: Bot, dispatcher: Dispatcher):
    notifications = []
    for item in db.notifications.find({'notification_type': "ratings"}):
        last_notification = datetime.fromisoformat(str(item['last_notification_datetime']))
        period = item['period']
        if last_notification <= datetime.utcnow() - timedelta(days=period):
            notification = {
                'user_id': item['user_id'],
                'chat_id': item['chat']['id'],
                'msg': configure_rating_notification(db.find_user(item['user_id'])['locale'], 7),
                'locale': db.find_user(item['user_id'])['locale']
            }
            notifications.append(notification)

    logging.info(f"Started sending notifications[ratings]... {len(notifications)}")

    for notification in notifications:
        try:
            await bot.send_message(notification['chat_id'], notification['msg'],
                                   parse_mode="HTML",
                                   disable_web_page_preview=True)

            db.update_notification(notification['user_id'], "ratings")
            db.set_user_state(notification['user_id'], state=Greeting.rating_page.state)

            state = db.get_user_state(user_id=notification['user_id'])
            storage_key = StorageKey(user_id=notification['user_id'], bot_id=int(BOT_ID),
                                     chat_id=notification['chat_id'])
            await dispatcher.storage.set_state(storage_key, state)

        except Exception as e:
            logging.error(f"Failed to send notification to {notification['user_id']}: {e}")

    await send_registration_proposal(bot, dispatcher)
