import datetime
from aiogram.types import Message, User, CallbackQuery, Chat
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
    
MONGODB_URL = os.getenv('MONGODB_URL')

client = MongoClient(MONGODB_URL)
db = client['pooolstop_webapp']
command_logs = db['command_logs']
callback_logs = db['callback_logs']
user_states = db['user_states']
user_collection = db['users']
notifications = db['notifications']
user_login_info = db['login_info']
workers_info = db['workers_info']
user_from_web_app = db['user_web_app']
user_watcher_link = db['user_watcher_link']


def _update_or_insert(collection, query, data):
    if collection.find_one(query):
        collection.update_one(query, {"$set": data})
    else:
        collection.insert_one(data)


def set_user_tokens_after_refresh(data, user_id):
    _update_or_insert(user_login_info, {'user_id': user_id}, {
        'access_token': data['accessToken'],
        'refresh_token': data['refreshToken']
    })


def set_user_tokens(data, login: str, password: str, user: User):
    login_info_data = {
        'user_id': user.id,
        'login': login,
        'password': password,
        'access_token': data['accessToken'],
        'refresh_token': data['refreshToken'],
        'last_login_datetime': datetime.datetime.utcnow(),
    }
    _update_or_insert(user_login_info, {'user_id': user.id}, login_info_data)


def get_user_tokens(user_id):
    info = user_login_info.find_one({'user_id': user_id})
    return {'access_token': info['access_token'], 'refresh_token': info['refresh_token']} if info else {
        'access_token': '', 'refresh_token': ''}


def user_notification_subscribe(user: User, chat: Chat, notification_type: str, period: int):
    notification_data = {
        'user_id': user.id,
        'chat': {'id': chat.id, 'type': chat.type},
        'notification_type': notification_type,
        'last_notification_datetime': datetime.datetime.utcnow(),
        'period': period
    }
    _update_or_insert(notifications, {'user_id': user.id, 'notification_type': notification_type}, notification_data)


def user_notification_unsubscribe(user: User, notification_type: str):
    notifications.delete_one({'user_id': user.id, 'notification_type': notification_type})


def update_notification(user_id: int, notification_type: str):
    current_time = datetime.datetime.utcnow()
    notifications.update_one({'user_id': user_id, 'notification_type': notification_type},
                             {'$set': {'last_notification_datetime': current_time}})


def add_user(user: User, chat: Chat):
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'linked': False,
        'email': "N/A",
        'locale': user.language_code,
        'chat': {'id': chat.id, 'type': chat.type}
    }
    _update_or_insert(user_collection, {'user_id': user.id}, user_data)


def set_user_locale(user: User, locale: str):
    user_collection.update_one({'user_id': user.id}, {'$set': {'locale': locale}})


def get_user_locale(user: User):
    userdb = user_collection.find_one({'user_id': user.id})
    return userdb['locale'] if userdb else None

def get_user_locale_by_id(user_id):
    userdb = user_collection.find_one({'user_id': user_id})
    return userdb['locale'] if userdb else None


def user_sync(user_id, email: str):
    user_collection.update_one({'user_id': user_id}, {'$set': {'linked': True, 'email': email}})


def user_sync_from_web_app(user_info):
    data = {
        "accessToken": user_info['accessToken'],
        "refresh_token": user_info['refresh_token'],
    }
    _update_or_insert(user_from_web_app, {'user_id': user_info['tg_id']}, data)


def user_desync(user_id):
    user_collection.update_one({'user_id': user_id}, {'$set': {'linked': False, 'email': ''}})


def check_user_profile_linked(user_id) -> bool:
    db_user = user_collection.find_one({'user_id': user_id})
    return db_user['linked'] if db_user else False


def set_user_state(user_id, state):
    user_collection.update_one({'user_id': user_id}, {'$set': {'state': state}})


def get_all_users():
    return user_collection.find({})


def get_user_state(user_id):
    user = user_collection.find_one({'user_id': user_id})
    return user['state'] if user else None


def find_user(user_id):
    return user_collection.find_one({'user_id': user_id})


def get_user_email(user_id):
    user_db = find_user(user_id)
    return user_db['email'] if user_db else None


def add_callback_log(callback: CallbackQuery):
    message_data = {
        'message_id': callback.message.message_id,
        'user_id': callback.from_user.id,
        'date': callback.message.date,
        'callback_data': callback.data
    }
    callback_logs.insert_one(message_data)


def add_command_log(message: Message):
    command_log = {
        'user_id': message.from_user.id,
        'command': message.text
    }
    command_logs.insert_one(command_log)


def get_user_watcher_link(user: User):
    wl = user_watcher_link.find_one({'user_id': user.id})
    return wl['watcher_link'] if wl else None

def set_user_watcher_link(user_id: int, link: str, watcher_id: int):
    data = {
        "user_id": user_id,
        "watcher_link": link,
        "watcher_id": watcher_id
    }
    _update_or_insert(user_watcher_link, {'user_id': user_id}, data)


def get_watcher_id(watcher_link):
    w_id = user_watcher_link.find_one({'watcher_link': watcher_link})
    return w_id['watcher_id'] if w_id else None