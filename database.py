import datetime
from aiogram.types import Message, User, CallbackQuery, Chat
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')

client = AsyncIOMotorClient(MONGODB_URL)
db = client['pooolstop_webapp']
command_logs = db['command_logs']
message_logs = db['message_logs']
custom_msg_logs = db['custom_msg_logs']
callback_logs = db['callback_logs']
user_states = db['user_states']
user_collection = db['users']
notifications = db['notifications']
user_login_info = db['login_info']
workers_info = db['workers_info']
user_from_web_app = db['user_web_app']
user_watcher_link = db['user_watcher_link']
user_ad_sources = db['user_ad_sources']


async def _update_or_insert(collection, query, data):
    if await collection.find_one(query):
        await collection.update_one(query, {"$set": data})
    else:
        await collection.insert_one(data)

async def set_user_tokens_after_refresh(data, user_id):
    await _update_or_insert(user_login_info, {'user_id': user_id}, {
        'access_token': data['accessToken'],
        'refresh_token': data['refreshToken']
    })


async def save_user_ad_source(user: User, source: str):
    query = {'user_id': user.id}
    if not await user_ad_sources.find_one(query):
        data = {
            'user_id': user.id,
            'timestamp': datetime.datetime.utcnow(),
            'source': source
        }
        await user_ad_sources.insert_one(data)


async def set_user_tokens(data, login: str, password: str, user: User):
    login_info_data = {
        'user_id': user.id,
        'login': login,
        'password': password,
        'access_token': data['accessToken'],
        'refresh_token': data['refreshToken'],
        'last_login_datetime': datetime.datetime.utcnow(),
    }
    await _update_or_insert(user_login_info, {'user_id': user.id}, login_info_data)

async def get_user_tokens(user_id):
    info = await user_login_info.find_one({'user_id': user_id})
    return {'access_token': info['access_token'], 'refresh_token': info['refresh_token']} if info else {
        'access_token': '', 'refresh_token': ''}

async def user_notification_subscribe(user: User, chat: Chat, notification_type: str, period: int):
    notification_data = {
        'user_id': user.id,
        'chat': {'id': chat.id, 'type': chat.type},
        'notification_type': notification_type,
        'last_notification_datetime': datetime.datetime.utcnow(),
        'period': period
    }
    await _update_or_insert(notifications, {'user_id': user.id, 'notification_type': notification_type}, notification_data)

async def user_notification_unsubscribe(user: User, notification_type: str):
    await notifications.delete_one({'user_id': user.id, 'notification_type': notification_type})

async def update_notification(user_id: int, notification_type: str):
    current_time = datetime.datetime.utcnow()
    await notifications.update_one({'user_id': user_id, 'notification_type': notification_type},
                                   {'$set': {'last_notification_datetime': current_time}})

async def add_user(user: User, chat: Chat):
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'linked': False,
        'email': "N/A",
        'locale': user.language_code,
        'is_premium': user.is_premium,
        'chat': {'id': chat.id, 'type': chat.type}
    }
    await _update_or_insert(user_collection, {'user_id': user.id}, user_data)

async def set_user_locale(user: User, locale: str):
    await user_collection.update_one({'user_id': user.id}, {'$set': {'locale': locale}})

async def get_user_locale(user: User):
    userdb = await user_collection.find_one({'user_id': user.id})
    return userdb['locale'] if userdb else None

async def get_user_locale_by_id(user_id):
    userdb = await user_collection.find_one({'user_id': user_id})
    return userdb['locale'] if userdb else None

async def get_user_scheduler(user_id):
    notification = await notifications.find_one({'user_id': user_id})
    if notification and notification['notification_type'] == 'ratings':
        return notification

async def user_sync(user_id, email: str):
    await user_collection.update_one({'user_id': user_id}, {'$set': {'linked': True, 'email': email}})

async def user_sync_from_web_app(user_info):
    data = {
        "accessToken": user_info['accessToken'],
        "refresh_token": user_info['refresh_token'],
    }
    await _update_or_insert(user_from_web_app, {'user_id': user_info['tg_id']}, data)

async def user_desync(user_id):
    await user_collection.update_one({'user_id': user_id}, {'$set': {'linked': False, 'email': ''}})

async def check_user_profile_linked(user_id) -> bool:
    db_user = await user_collection.find_one({'user_id': user_id})
    return db_user['linked'] if db_user else False

async def set_user_state(user_id, state):
    await user_collection.update_one({'user_id': user_id}, {'$set': {'state': state}})

async def get_all_users():
    cursor = user_collection.find({})
    users = await cursor.to_list(length=None)
    return users


async def get_user_state(user_id):
    user = await user_collection.find_one({'user_id': user_id})
    return user['state'] if user else None

async def find_user(user_id):
    return await user_collection.find_one({'user_id': user_id})

async def get_user_email(user_id):
    user_db = await find_user(user_id)
    return user_db['email'] if user_db else None

async def add_callback_log(callback: CallbackQuery):
    message_data = {
        'message_id': callback.message.message_id,
        'user_id': callback.from_user.id,
        'datetime': callback.message.date,
        'callback_data': callback.data
    }
    await callback_logs.insert_one(message_data)

async def add_command_log(message: Message):
    command_log = {
        'user_id': message.from_user.id,
        'command': message.text,
        'datetime': message.date,
    }
    await command_logs.insert_one(command_log)

async def add_message_log(message: Message):
    message_log = {
        'user_id': message.from_user.id,
        'message': message.text,
        'datetime': message.date,
    }
    await message_logs.insert_one(message_log)

async def get_user_watcher_link(user: User):
    wl = await user_watcher_link.find_one({'user_id': user.id})
    return wl['watcher_link'] if wl else None

async def set_user_watcher_link(user_id: int, link: str, watcher_id: int):
    data = {
        "user_id": user_id,
        "watcher_link": link,
        "watcher_id": watcher_id
    }
    await _update_or_insert(user_watcher_link, {'user_id': user_id}, data)

async def get_watcher_id(watcher_link):
    w_id = await user_watcher_link.find_one({'watcher_link': watcher_link})
    return w_id['watcher_id'] if w_id else None

async def log_custom_message(chat_id, message_text, message_type, status, error_message=None):
    message_log = {
        "chat_id": chat_id,
        "message_text": message_text,
        "message_type": message_type,
        "status": status,
        "error_message": error_message,
        "timestamp": datetime.datetime.utcnow()
    }
    await custom_msg_logs.insert_one(message_log)

async def log_bulk_send(potential_sends, successful_sends, message_text, message_type, results):
    bulk_log = {
        "potential_sends": potential_sends,
        "successful_sends": successful_sends,
        "message_text": message_text,
        "message_type": message_type,
        "timestamp": datetime.datetime.utcnow(),
        "results": results
    }
    await custom_msg_logs.insert_one(bulk_log)


async def is_user_admin(from_user: User):
    if from_user.id in [337508244, 382333146, 6693989343, 150235250]:
        return True
    else:
        return False