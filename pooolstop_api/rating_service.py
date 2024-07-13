import os
from xml.sax import parse

import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("RATING_SERVICE_BASE_URL")

headers = {
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
    "Access-Control-Allow-Origin": "*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjpbeyJhdXRob3JpdHkiOiJST0xFX1VTRVIifV0sImlkIjoyLCJzdWIiOiJ1c2VyIiwiaWF0IjoxNzE2NzYzNjk1LCJleHAiOjE3NDgyOTk2OTV9.cGXn2G0J1lOfZC25od2eb-y2Dd0yRlNoi7oTfRQp_U4",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.854 YaBrowser/24.4.2.854 (beta) Yowser/2.5 Safari/537.36",
}


def parse_pool(pool, index):
    pool_data = {
        'rating': int(index),
        'pool': str(pool['pool_name']),
        'pool_url': str(pool['pool_url']),
        'payrate': float(pool['avr_pay_rate']),
        'percent': float(pool['percent'])
    }
    return pool_data


def get_ratings_for_table(period: int, u: str = "th"):
    querystring = {"period": str(period), "unit": u}
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)
    response_json = response.json()
    data = []
    index = 1
    for pool in response_json:
        data.append(parse_pool(pool, index))
        index = index + 1
    return data
