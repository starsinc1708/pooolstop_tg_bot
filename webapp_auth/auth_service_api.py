from aiohttp import web
import aiohttp_cors
from pymongo import MongoClient
import asyncio
import os
from dotenv import load_dotenv

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


async def sync_telegram_user(request):
    try:
        print("sync_telegram_user")
        request_body = await request.text()
        if not request_body:
            raise ValueError("Request body is empty")

        print("Request body:", request_body)

        user_info = await request.json()
        if not user_info:
            raise ValueError("Failed to parse JSON from request body")

        await asyncio.to_thread(user_sync_from_web_app, user_info)

        response = {
            "code": 200,
            "message": "",
            "status": "success",
            "data": ""
        }
        return web.json_response(response, status=200)
    except Exception as e:
        print("Error:", str(e))
        response = {
            "code": 400,
            "message": str(e),
            "status": "error",
            "data": ""
        }
        return web.json_response(response, status=400)


async def delete_telegram_user(request):
    try:
        print("delete_telegram_user")

        # Проверка содержимого запроса
        request_body = await request.text()
        if not request_body:
            raise ValueError("Request body is empty")

        print("Request body:", request_body)

        user_info = await request.json()
        if not user_info:
            raise ValueError("Failed to parse JSON from request body")

        await asyncio.to_thread(desync_from_web_app, user_info)

        response = {
            "code": 200,
            "message": "",
            "status": "success",
            "data": user_info.get('tg_id')
        }
        return web.json_response(response, status=200)
    except Exception as e:
        print("Error:", str(e))
        response = {
            "code": 400,
            "message": str(e),
            "status": "error",
            "data": ""
        }
        return web.json_response(response, status=400)


async def check_telegram_user_synced(request):
    try:
        print("check_telegram_user_synced")

        request_body = await request.text()
        if not request_body:
            raise ValueError("Request body is empty")

        print("Request body:", request_body)

        user_info = await request.json()
        if not user_info:
            raise ValueError("Failed to parse JSON from request body")

        data = await asyncio.to_thread(get_user_web_app, user_info)
        print(data)
        if data:
            response = {
                "code": 200,
                "message": "",
                "status": "success",
                "data": {
                    "accessToken": data['accessToken'],
                    "refreshToken": data['refreshToken'],
                    "tg_id": data['tg_id']
                }
            }
            return web.json_response(response, status=200)
        else:
            response = {
                "code": 400,
                "message": "no such user in db",
                "status": "not found",
                "data": ""
            }
            return web.json_response(response, status=200)
    except Exception as e:
        print("Error:", str(e))
        response = {
            "code": 400,
            "message": str(e),
            "status": "error",
            "data": ""
        }
        return web.json_response(response, status=400)


app = web.Application()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

cors.add(app.router.add_post('/api/create/tgsync', sync_telegram_user))
cors.add(app.router.add_post('/api/delete/tgsync', delete_telegram_user))
cors.add(app.router.add_post('/api/tgsync', check_telegram_user_synced))

if __name__ == '__main__':
    web.run_app(app, port=8003)
