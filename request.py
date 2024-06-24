import json
import random
from time import sleep

import requests
from mysql.connector import connect, Error
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()

def create_connection():
    """建立連接"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection


def register_landlord(username, phonenum, password):
    url = 'http://127.0.0.1:5000/api/signup'
    data = {
        'username': username,
        'phonenum': phonenum,
        'password': password,
        'type': 'landlord'
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("Landlord registered successfully")
    else:
        print(f"Failed to register landlord: {response.content}")
    return response.status_code == 201


def login_landlord(username, password):
    url = 'http://127.0.0.1:5000/api/login'
    data = {
        'username': username,
        'password': password,
        'type': 'landlord'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        jwt = response.content.decode('utf-8')
        jwt = json.loads(jwt)
        return jwt['access_token']
    else:
        print(f"Failed to login: {response.content}")
        return None


def post_rental(data, token):
    url = 'http://127.0.0.1:5000/api/rental'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("Rental added successfully")
    else:
        print(f"Failed to add rental: {response.content}")


def fetch_rental_data(page):
    url = 'https://rent.591.com.tw/home/search/rsList'
    payload = {
        'is_format_data': 1,
        'is_new_list': page,
        'type': 1,
        'region': 1,
        'section': '1,2,3',
        'kind': 1,
        'searchtype': 1,
        'recom_community': 1
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Connection': 'keep-alive',
        # TODO: Replace these with your own values
        'Cookie': 'T591_TOKEN=htl2rt26sutg9pltej6ibt053h; rentPreventFraud=0; webp=1; PHPSESSID=4topmdqudb5tfk5ac4fcehmqdf; urlJumpIp=1; newUI=1; tw591__privacy_agree=0; new_rent_list_kind_test=0; house_detail_stat=%5B%7B%22type%22%3A%221%22%2C%22resource%22%3A%228%22%2C%22post_id%22%3A%2216857107%22%7D%5D; timeDifference=-1; XSRF-TOKEN=eyJpdiI6InlYOFNSZCtLV1VzOUh4ekdVeUZCQnc9PSIsInZhbHVlIjoiNWQ4SE9YbEZMWTlXOVlsd0xldlBocDBhdTN2dUk2d3c4MnlKNVd1eWl3bDRlYmR1OEVnaWZVOFRNeENjWXVtcXVqeDBVdGJyYm0wYllGZXVaZmF5SjdWOTluNGdyanliTXNaekNWRHR3azF3NWFudHEyZ0g4RXpjV3JhYTRTSUYiLCJtYWMiOiJmNjQ2ZTAzZjllOWI0NWUzMzZmNjAyMWRlNDNlODhlOTI3Y2Q3ZGFlOWIyMTg3MWJjNGEwY2U4ZWU0ZDEzOTI1IiwidGFnIjoiIn0%3D; 591_new_session=eyJpdiI6Ik13WGEwRUdDeUN4b3FoRWpCWlBHWEE9PSIsInZhbHVlIjoiTmErS0JRcThLenpJZHNuUjlKR2pLYWw1WTVGRmhxWHc5UXhSRG1kVHAwMmRVVEpHY3phRnJkZ0dGUk1EdXBrRWJSaUp3VVU3L2lVZytIZ3JONHJQaDVBQkEyU1IvYUtYdTlKZnRBMEZTNFNGUzFscDF4dlNua2pnbVRkOVNCRUMiLCJtYWMiOiIwY2IxMzA1NTIzNDgzNGIxYmFmMWM4MjQyNDMwOTk5MDYyNDAwZWEzOWU0MDViMDk4YmQ1ZTNiYjI3ZDFhYzJmIiwidGFnIjoiIn0%3D',
        'Device': 'pc',
        # TODO: Replace these with your own values
        'Deviceid': 'htl2rt26sutg9pltej6ibt053h',
        'Host': 'rent.591.com.tw',
        'Referer': 'https://rent.591.com.tw/?region=1&section=3,9,12&kind=1&searchtype=1',
        'Sec-Ch-Ua': '"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        # TODO: Replace these with your own values
        'X-Csrf-Token': 'OtkdSswr0cBHRdFZRJ1inXecyXHCpelMby52xzGB',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.get(url, params=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def process_and_insert_data(username, phonenum, password):
    if not register_landlord(username, phonenum, password):
        return

    token = login_landlord(username, password)
    if token is None:
        return

    for page in range(6, 20):
        rental_data = fetch_rental_data(page)
        print(rental_data)
        if rental_data is None or not rental_data.get('data', {}).get('topData', []):
            continue

        for rental in rental_data['data']['topData']:
            address = rental['section_name'] + ' ' + rental['street_name']
            title = rental['title']
            price = int(rental['price'].replace(',', ''))
            # type_ = rental['type']
            type_ = random.choice(['整層', '套房', '雅房'])
            room_str = rental['room_str']
            bedroom = int(room_str[0]) if '房' in room_str else 0
            if '房' in room_str:
                room_str = room_str.split('房')[1]
            living_room = int(room_str[0]) if '廳' in room_str else random.randint(0, 2)
            if '廳' in room_str:
                room_str = room_str.split('廳')[1]
            bathroom = int(room_str[0]) if '衛' in room_str else random.randint(0, 3)
            if '衛' in room_str:
                room_str = room_str.split('衛')[1]
            ping = float(rental['area'])
            rental_term = rental['rent_tag'][0]['name'] if rental['rent_tag'] else '未知'
            post_date = datetime.now().strftime('%Y-%m-%d')

            data = {
                'address': address,
                'title': title,
                'price': price,
                'type': type_,
                'bedroom': bedroom,
                'living_room': living_room,
                'bathroom': bathroom,
                'ping': ping,
                'rental_term': rental_term,
                'post_date': post_date
            }
            post_rental(data, token)


if __name__ == '__main__':
    username = f'test_landlord_{random.randint(1000, 9999)}'
    phonenum = '0912345678'
    password = '123456'
    process_and_insert_data(username, phonenum, password)
