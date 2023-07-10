import requests
import json
import os
from datetime import datetime

BASE_URL = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"


def update_user_sign():
    print("Updating User-Sign and Timestamp")  # Added logging
    headers_api_url = "https://suheylsbusiness.com/wp-json/tiktok/v1/data"
    response = requests.get(headers_api_url)
    headers_string = response.text

    # Find the last occurrence of 'user-sign:' and extract its value
    last_user_sign_pos = headers_string.rfind('user-sign:')
    last_user_sign_value = headers_string[last_user_sign_pos + 10:].split()[0]

    # Find the last occurrence of 'timestamp:' and extract its value
    last_timestamp_pos = headers_string.rfind('timestamp:')
    last_timestamp_value = headers_string[last_timestamp_pos + 10:].split()[0]

    HEADERS["user-sign"] = last_user_sign_value
    HEADERS["timestamp"] = last_timestamp_value

    print("User-Sign and Timestamp updated successfully")  # Added logging

def send_data_to_api(type, data):
    url = "http://18.192.212.32/api/data"
    payload = {"type": type, "data": data}
    response = requests.post(url, json=payload)
    if response.status_code == 201:
        print("Data sent successfully!")
    else:
        print(f"Error: {response.status_code}")

PERIODS = [7, 30, 120]
COUNTRIES = ["DE", "US", "IN"]
INDUSTRIES = [24000000000, 26000000000, 28000000000]
NEW_ON_BOARD = True
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

# Loop through periods, countries, and industries
# Create the output directory if it doesn't exist
os.makedirs("Outputs", exist_ok=True)

# Loop through periods, countries, and industries
for period in PERIODS:
    for country in COUNTRIES:
        update_user_sign()
        for industry in INDUSTRIES:
            print(f"Processing data for period {period}, country {country}, industry {industry}...")

            # Set parameters
            params = {
                "page": 1,
                "limit": 3,
                "period": period,
                "industry_id": industry,
                "country_code": country,
            }
            if NEW_ON_BOARD:
                params["filter_by"] = "new_on_board"

            # Send GET request to the API
            response = requests.get(BASE_URL, params=params, headers=HEADERS)

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()

                # Pagination logic
                while data['data']['pagination']['has_more']:
                    print(f"Processing page {params['page']}")
                    params['page'] += 1
                    response = requests.get(BASE_URL, params=params, headers=HEADERS)
                    if response.status_code == 200:
                        new_data = response.json()
                        # Check if we have reached the server's hardcoded limit
                        if new_data.get('code') == 40000:
                            print("Reached server's hardcoded limit. Moving to the next set of parameters.")
                            break
                        data['data']['list'].extend(new_data['data']['list'])
                    else:
                        print("Error while paginating. Moving to the next set of parameters.")
                        break

                # Save the data to a JSON file in the Outputs directory
                filename = os.path.join("Outputs", f"hashtag_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")
                with open(filename, 'w') as f:
                    json.dump(data['data']['list'], f, indent=4)
                print(f"Data saved to {filename}")
                print("Sending data to API...")  # Added logging
                send_data_to_api('hashtag', data['data']['list']) # Send data to the Node.js API
                print("Data sent to API successfully")  # Added logging
            else:
                print(f"Error {response.status_code}. Moving to the next set of parameters.")
