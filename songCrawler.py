import requests
import json
import os
from datetime import datetime

BASE_URL = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/sound/rank_list"
HEADERS = {
  'accept': 'application/json, text/plain, */*',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9',
  'anonymous-user-id': '46984e1180a847878f6e7c9e7382b172',
  'cookie': 'lang_type=en; _ga=GA1.1.501082322.1688630383; s_v_web_id=verify_ljquxjm8_4wFKwdZG_Pln2_4Eiu_9mI1_5REz8WFscUeM; cookie-consent={%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}; ttwid=1%7CckpcKz3NQ7wHcrCm8QxbnHHc6nhao4ZOqQoPIafkyNs%7C1688630750%7Cfd142b33c7ec2695c5ceadbb787cc3949e1e1e9e415c68f1dfa1d1e7d0b24276; _ga_QQM0HPKD40=GS1.1.1688630382.1.1.1688630752.0.0.0; msToken=qwxs5hFjOfppMwl55uJK4daNVSgI10Lv9K3neWXl4xPjJCkiSg8C-30i0iiF5zoKk5Kd0iQZ3YxwNPK_1iZ9QjmKa1Mzxs7KN4feCmglNf8BoLCF2OPR5j-EMBW8gLQ=; msToken=qwxs5hFjOfppMwl55uJK4daNVSgI10Lv9K3neWXl4xPjJCkiSg8C-30i0iiF5zoKk5Kd0iQZ3YxwNPK_1iZ9QjmKa1Mzxs7KN4feCmglNf8BoLCF2OPR5j-EMBW8gLQ=',
  'lang': 'en',
  'referer': 'https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en',
  'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'timestamp': '1688630753',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
  'user-sign': '3feb2b2ddfd419bc',
  'web-id': '7252612203529815554'
}

NEW_ON_BOARD = False
COMMERCIAL_MUSIC = True
RANK_TYPE = 'popular' # this can be either "surging" or "popular"
PERIOD = 7
COUNTRY = 'DE'
PAGE_SIZE = 3

def update_user_sign():
    print("Updating User-Sign and Timestamp")
    headers_api_url = "https://suheylsbusiness.com/wp-json/tiktok/v1/data"
    response = requests.get(headers_api_url)
    headers_string = response.text

    last_user_sign_pos = headers_string.rfind('user-sign:')
    last_user_sign_value = headers_string[last_user_sign_pos + 10:].split()[0]

    last_timestamp_pos = headers_string.rfind('timestamp:')
    last_timestamp_value = headers_string[last_timestamp_pos + 10:].split()[0]

    HEADERS["user-sign"] = last_user_sign_value
    HEADERS["timestamp"] = last_timestamp_value

    print("User-Sign and Timestamp updated successfully")

def get_trending_data():
    print("Fetching trending data")
    page = 1
    has_more = True
    result = []

    while has_more:
        print(f"Processing page {page}")
        payload = {
            'period': PERIOD,
            'page': page,
            'limit': PAGE_SIZE,
            'rank_type': RANK_TYPE,
            'new_on_board': NEW_ON_BOARD,
            'commercial_music': COMMERCIAL_MUSIC,
            'country_code': COUNTRY
        }

        response = requests.get(BASE_URL, headers=HEADERS, params=payload)
        data = response.json()

        if 'data' not in data or 'sound_list' not in data['data'] or 'pagination' not in data['data']:
            break

        result.extend(data['data']['sound_list'])

        pagination = data['data']['pagination']
        has_more = pagination['has_more']
        page += 1

    print("Trending data fetch completed")
    return result

def save_to_file(data, filename):
    print(f"Saving data to file: {filename}")
    os.makedirs("Outputs", exist_ok=True)

    with open(f"Outputs/{filename}", 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Data saved successfully")

    send_data_to_api('song', data) # Send data to the Node.js API

def send_data_to_api(type, data):
    url = "http://18.192.212.32/api/data"
    payload = {"type": type, "data": data}
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("Data sent successfully!")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    update_user_sign()
    data = get_trending_data()
    save_to_file(data, f"song_data_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.json")