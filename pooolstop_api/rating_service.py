import requests

url = "https://poools.top/api/rank/top"

headers = {
    "Accept": "*/*",
    "Accept-Language": "ru,en;q=0.9",
    "Access-Control-Allow-Origin": "*",
    "Authorization": "x-code smhpool",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Referer": "https://poools.top/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.854 YaBrowser/24.4.2.854 (beta) Yowser/2.5 Safari/537.36",
    "^sec-ch-ua": "^\^Chromium^^;v=^\^122^^, ^\^Not",
    "sec-ch-ua-mobile": "?0",
    "^sec-ch-ua-platform": "^\^Windows^^^"
}


def parse_pool(pool, index):
    pool_data = {
        'rating': int(index),
        'pool': str(pool['pool']),
        'pool_url': str(pool['pool_url']),
        'payrate': float(pool['avrRate'])
    }
    return pool_data


def get_ratings_for_table(period: int, u: str = "th"):
    querystring = {"p": str(period), "u": u}
    response_json = requests.request("GET", url, headers=headers, params=querystring, verify=False).json()
    data = []
    index = 1
    for pool in response_json:
        data.append(parse_pool(pool, index))
        index = index + 1
    return data
