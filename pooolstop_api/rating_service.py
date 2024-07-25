import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import database as db

load_dotenv()

url = os.getenv("RATING_SERVICE_BASE_URL")
add_watcher_url = os.getenv("RATING_SERVICE_ADD_WATCHER")
jwt_token = os.getenv("RATING_JWT_TOKEN")


headers = {
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
    "Access-Control-Allow-Origin": "*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {jwt_token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.854 YaBrowser/24.4.2.854 (beta) Yowser/2.5 Safari/537.36",
}


def parse_pool(pool, index):
    if index > 1:
        pool_data = {
            'rating': int(index),
            'pool': str(pool['pool_name']),
            'pool_url': str(pool['pool_url']),
            'payrate': float(pool['avr_pay_rate']),
            'is_user': pool['is_user'],
            'percent': float(pool['percent']) - 100.0
        }
    else:
        pool_data = {
            'rating': int(index),
            'pool': str(pool['pool_name']),
            'pool_url': str(pool['pool_url']),
            'payrate': float(pool['avr_pay_rate']),
            'is_user': pool['is_user'],
            'percent': float(pool['percent'])
        }
    return pool_data


def parse_pool_with_watcher(pool, index, user_rate):
    if pool['is_user']:
        pool_data = {
            'rating': int(index),
            'pool': str(pool['pool_name']),
            'pool_url': str(pool['pool_url']),
            'payrate': float(pool['avr_pay_rate']),
            'is_user': pool['is_user'],
            'percent': 100.0
        }
    else:
        diff = (float(pool['avr_pay_rate']) / user_rate * 100)  - 100
        if 0.01 > diff > -0.01:
            diff = 0.0

        pool_data = {
            'rating': int(index),
            'pool': str(pool['pool_name']),
            'pool_url': str(pool['pool_url']),
            'payrate': float(pool['avr_pay_rate']),
            'is_user': pool['is_user'],
            'percent': diff
        }
    return pool_data


async def get_ratings_for_table(period: int, u: str = "th"):
    querystring = {"period": str(period), "unit": u}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_json = await response.json()
            data = []
            index = 1
            for pool in response_json:
                data.append(parse_pool(pool, index))
                index += 1
    return data, -1


async def get_ratings_for_table_with_watcher(watcher_link: str, period: int, u: str = "th"):
    watcher_id = await db.get_watcher_id(watcher_link)
    if not watcher_id:
        link = {"link": watcher_link}
        async with aiohttp.ClientSession() as session:
            async with session.post(add_watcher_url, json=link, headers=headers) as response:
                response_json = await response.json()
                watcher_id = response_json.get('watcher_id', None)

    querystring = {"period": str(period), "unit": u, "watcher_id": watcher_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_json = await response.json()
            data = []
            index = 1
            user_rate = 0
            for pool in response_json:
                if pool['is_user']:
                    user_rate = float(pool['avr_pay_rate'])

            if user_rate == 0:
                for pool in response_json:
                    data.append(parse_pool(pool, index))
                    index += 1
            else:
                for pool in response_json:
                    data.append(parse_pool_with_watcher(pool, index, user_rate))
                    index += 1
    return data, watcher_id if watcher_id else -1
