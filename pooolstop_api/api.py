import time
import requests
import database as db

API_URL = "https://lk.poools.top/api/v1/"


async def get_balance(user_id):
    url = API_URL + "balance"
    tokens = db.get_user_tokens(user_id)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {tokens['access_token']}",
        "Connection": "keep-alive",
        "Cookie": f"b24_sitebutton_hello=y; accessToken={tokens['access_token']}; refreshToken={tokens['refresh_token']}",
        "Referer": "https://lk.poools.top/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.462 YaBrowser/24.4.5.462 (beta) Yowser/2.5 Safari/537.36",
        "^sec-ch-ua": "^\^Chromium^^;v=^\^122^^, ^\^Not",
        "sec-ch-ua-mobile": "?0",
        "^sec-ch-ua-platform": "^\^Windows^^^"
    }
    response = requests.request("GET", url,
                                headers=headers).json()

    if response['status'] == 'success':
        return response['data']
    else:
        return {"totalUsdt": "N\A", "totalBtc": "N\A"}


async def get_statistics(user_id):
    url = API_URL + "dashboard"
    tokens = db.get_user_tokens(user_id)

    payload = {
        "start": round(time.time() * 1000),
        "step": 0
    }

    print(payload['start'])
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {tokens['access_token']}",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": f"b24_sitebutton_hello=y; accessToken={tokens['access_token']}; refreshToken={tokens['refresh_token']}",
        "Origin": "https://lk.poools.top",
        "Referer": "https://lk.poools.top/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.462 YaBrowser/24.4.5.462 (beta) Yowser/2.5 Safari/537.36",
        "^sec-ch-ua": "^\^Chromium^^;v=^\^122^^, ^\^Not",
        "sec-ch-ua-mobile": "?0",
        "^sec-ch-ua-platform": "^\^Windows^^^"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code == 401:
        return {"total": "N\A",
                "active": "N\A",
                "warning": "N\A",
                "dead": "N\A"}

    response = response.json()

    if response['status'] == 'success':
        return response['data']['minersInfo'], response['data']['chart']['totalHashrate'],
    else:
        return {"total": "N\A",
                "active": "N\A",
                "warning": "N\A",
                "dead": "N\A"}


def get_worker_icon(worker):
    if worker['active']:
        return "✅"
    if not worker['active']:
        return "❌"


async def get_workers_table(user_id):
    url = API_URL + "miners"
    tokens = db.get_user_tokens(user_id)

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en;q=0.9",
        "Authorization": f"Bearer {tokens['access_token']}",
        "Connection": "keep-alive",
        "Cookie": f"accessToken={tokens['access_token']}; refreshToken={tokens['refresh_token']}; b24_sitebutton_hello=y",
        "Referer": "https://lk.poools.top/workers",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.1837 YaBrowser/24.6.0.1837 (beta) Yowser/2.5 Safari/537.36",
        "^sec-ch-ua": "^\^Chromium^^;v=^\^124^^, ^\^YaBrowser^^;v=^\^24^^, ^\^Not-A.Brand^^;v=^\^99^^^",
        "sec-ch-ua-mobile": "?0",
        "^sec-ch-ua-platform": "^\^Windows^^^"
    }

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 401:
        return "Can't load Workers Info - visit lk.poools.top/workers"

    response = response.json()

    if response['status'] == 'success':
        data = []
        sum_current = 0
        sum_hashrate_24h = 0
        sum_hashrate_1h = 0
        for worker in response['data']:
            sum_current = sum_current + worker['hashCurrent']
            sum_hashrate_1h = sum_hashrate_1h + worker['hash1Hour']
            sum_hashrate_24h = sum_hashrate_24h + worker['stat24h']['hashrate']
            info = {
                'id': worker['id'],
                'icon': get_worker_icon(worker),
                'name': worker['name'],
                'hashCurrent': worker['hashCurrent'],
                'hash1Hour': worker['hash1Hour'],
                'hash24Hour': worker['stat24h']['hashrate'],
                'info': worker['info'],
                'tags': ["#" + tag['name'] for tag in worker['tags']]
            }
            data.append(info)
        total_info = f"Current: <b>{sum_current}</b> TH\nHASHRATE/1h: <b>{sum_hashrate_1h}</b> TH\nHASHRATE/24H: <b>{sum_hashrate_24h}</b> TH"
        # table = table + f"\n[{get_worker_icon(worker)}] [{worker['name']}] \nCurrent: <b>{worker['hashCurrent']}</b> TH | <b>{worker['hash1Hour']}</b> TH/1h | <b>{worker['stat24h']['hashrate']}</b> TH/24h"
        return data, total_info
    else:
        return "Can't load Workers Info - visit lk.poools.top/workers"
