import os
import requests
from aiogram.types import User, Chat
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("RANK_API")
jwt_token = os.getenv("RATING_JWT_TOKEN")


headers = {
    "accept": "*/*",
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json"
}

def prepare_scheduler_period(period):
    scheduler_period = "DAY"
    if period == 1:
        scheduler_period = "DAY"
    elif period == 7:
        scheduler_period = "WEEK"
    elif period == 30:
        scheduler_period = "MONTH"
    return scheduler_period

def prepare_data(user: User, chat: Chat, scheduler=False, scheduler_period="", pool_period=0, show_watcher=False):
    data = {
        'chatId': chat.id,
        'isBot': user.is_bot,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'userName': user.username,
        'languageCode': user.language_code,
        'scheduler': scheduler,
        'schedulerPeriod': scheduler_period,
        'poolPeriod': pool_period,
        'showWatcher': show_watcher,
    }
    return data


def send_request(user_id, data):
    response = requests.put(f"{url}/api/telegram/save-or-update/{user_id}", json=data, headers=headers)
    return response

def add_user(user: User, chat: Chat):
    data = prepare_data(user, chat)
    send_request(user.id, data)

def add_scheduler(user: User, chat: Chat, scheduler_period):
    scheduler_period = prepare_scheduler_period(scheduler_period)
    data = prepare_data(user, chat, scheduler=True, scheduler_period=scheduler_period, pool_period=7)
    send_request(user.id, data)

def delete_scheduler(user: User, chat: Chat):
    data = prepare_data(user, chat, scheduler=False, scheduler_period="", pool_period=0)
    send_request(user.id, data)

# def add_watcher(user: User, chat: Chat):
#     scheduler = db.get_user_scheduler(user.id)
#     scheduler_period = prepare_scheduler_period(scheduler['period'])
#     data = prepare_data(user, chat, scheduler=True, scheduler_period=scheduler_period, pool_period=7)
#     send_request(user.id, data)
