import requests
import json
import os
from datetime import datetime

BASE_URL = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/sound/rank_list"
HEADERS = {
  'accept': 'application/json, text/plain, */*',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9',
  'anonymous-user-id': '471fb0de-4365-474b-a9f7-6e6eb7d3070e',
  'cookie': 'lang_type=en; _ga=GA1.1.2040895266.1690291270; s_v_web_id=verify_lkibs6n8_bBnFeckL_Hl0z_4vXC_ANwo_RjrjQk3maAhK; cookie-consent={%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22criteo%22:true%2C%22version%22:%22v9%22}; ttwid=1%7Cpu5akhMQEtxxRxbV8zkKMG4iEr9Gjk6hqgxrsClBUuk%7C1690315956%7Cc1701581043f71dba9e3b4d37dad6c31d0d22f5bb46d3ff8053186a18a209307; msToken=_77QjhOlbinayQbrL-i1la9zI6ZyMRH0EkvqSSW9o8NN4xEyJ7pQ00yMogiFzPftcaZwTrr4xIz4T1xKC4gqCDPOwocaFSG-sEXrII5VQH1W5aTBQrLvBu4m2-ZSZrg=; msToken=dC9c96XwvhC65S0kNofLZQh_dzxQdTMCArCVLm5fZoQJrUCvj93gJHrEiK5KTGRnrXqIQKy2kaOIaRI-Jm_njWDYFv4e0J7F9a9gRpr09zoSL2-ND9a4K5U1d5Od6Tpavxf9Gvk1B5roXtI=; _ga_QQM0HPKD40=GS1.1.1690291270.1.1.1690315974.40.0.0',
  'lang': 'en',
  'referer': 'https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en',
  'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'timestamp': '1690315979',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
  'user-sign': '1b04a737fef89c03',
  'web-id': '7259745681661003266'
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

    web_id_pos = headers_string.rfind('web-id:')
    web_id = headers_string[web_id_pos + 10:].split()[0]

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

        # Add parameters to each data point
        for entry in data['data']['sound_list']:
            entry['period'] = PERIOD
            entry['country'] = COUNTRY
            entry['commercial_music'] = COMMERCIAL_MUSIC
            entry['new_on_board'] = NEW_ON_BOARD
            entry['rank_type'] = RANK_TYPE

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
    url = "http://18.192.212.32/api/data?API=22FFF861F9169F9BCD816662549BCE07A7983C4BC11AC403478A0FDBF632F9A3"
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