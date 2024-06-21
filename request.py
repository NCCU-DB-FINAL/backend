import json
import random
import requests
from mysql.connector import connect, Error
from datetime import datetime

def create_connection():
    """建立連接"""
    connection = None
    try:
        connection = connect(
            host='mysql.h9bxbshbg9f4bjb9.japaneast.azurecontainer.io',
            user='root',
            password='nccunccunccu',
            database='rental_db'
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


def fetch_rental_data():
    url = 'https://rent.591.com.tw/home/search/rsList'
    payload = {
        'is_format_data': 1,
        'is_new_list': 3,
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
        'Cookie': 'T591_TOKEN=htl2rt26sutg9pltej6ibt053h; rentPreventFraud=0; webp=1; PHPSESSID=4topmdqudb5tfk5ac4fcehmqdf; urlJumpIp=1; new_rent_list_kind_test=1; newUI=1; tw591__privacy_agree=0; XSRF-TOKEN=eyJpdiI6IkhzVDdubmdDdU5KZnptbTgwc3hoNlE9PSIsInZhbHVlIjoiUmZLeWU0TjgxeUJMZnl2U0o5VWloVHUzMjZjeU43akhkZUMyc1VxTG8zTUQ0cXRLSlJKdFZ6Z1hNMnFZbDBLSmxVVWl4TDB4d05aTkFzendIV3FVVWl0M0pUcXFJZ29SK3h6QjVXaUdGQ296Ry9qN3E5eUFiSktnMU45Y3B2RHAiLCJtYWMiOiJhY2NkZmZmZGYwYWU4ZTM5ZjE2NWU3OTcwY2JlZGMwMjYwYTJhNTlhNmQ3NzBmMWExOWFlMGQ2MTM4OGE3MWUwIiwidGFnIjoiIn0%3D; 591_new_session=eyJpdiI6InhMOWpIYVJLSy9vYXZUOWR0SitKS1E9PSIsInZhbHVlIjoiZ0ZjZnVwZ3NtQTF4aHB6bGRUQXFrbEtyTnFYT0V5WkYzTGtNQ1dBUjZwZGdUL3I5Si80TTY4SFRkK3phKzJkeS9NaDVVa05tVStsbHBXVm5uM3IxQ3VEOUJKekQyMnQzVW13QnJ3MnZmcjJvRVkwanN1akQzcUlCbmxwNG8xMy8iLCJtYWMiOiIzYjI5MzRjYzgwMTA5OTBlNDlmYzA4YWE3NjQxYTBmZTE5NTk3MzY5ZGE1NTFjNTkwZDQ1Y2RmMjNkNjZmMzFiIiwidGFnIjoiIn0%3D; timeDifference=0',
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
        'X-Csrf-Token': 'hTCq6mdhZFohZhvQIJoBllliiPtSVLJmbojI1rGp',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.get(url, params=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def process_and_insert_data(username, phonenum, password):
    rental_data = fetch_rental_data()
    print(rental_data)
    if rental_data is None or not rental_data.get('data', {}).get('topData', []):
        return

    if not register_landlord(username, phonenum, password):
        return

    token = login_landlord(username, password)
    if token is None:
        return

    for rental in rental_data['data']['topData']:
        address = rental['section_name'] + ' ' + rental['street_name'] + ' ' + rental['title']
        price = int(rental['price'].replace(',', ''))
        # type_ = rental['type']
        type_ = '整層'
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