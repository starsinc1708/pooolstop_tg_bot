from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
client = MongoClient(MONGODB_URL)
db = client['pooolstop_webapp']
user_from_web_app = db['user_web_app']
user_collection = db['users']

def user_sync(user_id, email: str):
    user_collection.update_one({'user_id': user_id}, {'$set': {'linked': True, 'email': email}})

def user_desync(user_id):
    user_collection.update_one({'user_id': user_id}, {'$set': {'linked': False, 'email': ''}})

def user_sync_from_web_app(user_info):
    db_user = user_from_web_app.find_one({'user_id': user_info['tg_id']})
    if db_user:
        data = {
            "email": user_info['email'],
            "accessToken": user_info['accessToken'],
            "refreshToken": user_info['refreshToken'],
        }
        user_from_web_app.update_one({'user_id': user_info['tg_id']}, {'$set': data})
    else:
        data = {
            "user_id": user_info['tg_id'],
            "username": user_info['username'],
            "firstName": user_info['firstName'],
            "secondName": user_info['secondName'],
            "email": user_info['email'],
            "accessToken": user_info['accessToken'],
            "refreshToken": user_info['refreshToken'],
        }
        user_from_web_app.insert_one(data)
    user_sync(user_info['tg_id'], user_info['email'])

def get_user_web_app(info):
    db_user = user_from_web_app.find_one({'user_id': info['tg_id']})
    if db_user:
        return {'accessToken': db_user['accessToken'],
                'refreshToken': db_user['refreshToken'],
                'tg_id': db_user['user_id']}

def desync_from_web_app(info):
    db_user = user_from_web_app.find_one({'user_id': info['tg_id']})
    if db_user:
        user_from_web_app.delete_one({'user_id': info['tg_id']})


def get_user_by_chat_id(chat_id):
    return user_collection.find_one({"chat.id": int(chat_id)})