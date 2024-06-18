import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime


def create_connection():
    """建立連接"""
    connection = None
    try:
        connection = mysql.connector.connect(
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


def insert_rental(data):
    connection = create_connection()
    if connection is None:
        return
    cursor = connection.cursor()
    query = """
        INSERT INTO Rental (Address, Price, Type, Bedroom, LivingRoom, Bathroom, Ping, RentalTerm, PostDate, L_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Data inserted successfully")
    except Error as e:
        print(f"Failed to insert data: {e}")
    finally:
        cursor.close()
        connection.close()


def fetch_rental_data():
    url = 'https://rent.591.com.tw/home/search/rsList'
    payload = {
        'is_format_data': 1,
        'is_new_list': 1,
        'type': 1,
        'region': 1,
        'section': '3,9,12',
        'kind': 1,
        'searchtype': 1,
        'recom_community': 1
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'webp=1; PHPSESSID=htl2rt26sutg9pltej6ibt053h; urlJumpIp=1; T591_TOKEN=htl2rt26sutg9pltej6ibt053h; newUI=1; tw591__privacy_agree=0; timeDifference=-1; house_detail_stat=%5B%7B%22type%22%3A%221%22%2C%22resource%22%3A%228%22%2C%22post_id%22%3A%2216741838%22%7D%5D; rentPreventFraud=0; new_rent_list_kind_test=0; XSRF-TOKEN=eyJpdiI6InlDNDhad2NnWktaNUJZQWtTWUgxZFE9PSIsInZhbHVlIjoiSWJLZGRJZ3RpVjhlRG5HVWkvN2VEb1JJSVh3YnhPWTdmTFE5Q1JSaGJMK01EN2JGbnJRWmpzVS9FRlVrVUpaRjFaOGRBbGdKRUwxSFI4YVZtSzc4OHVVSU9ySkF4ZmNiQmFYVDlMZWZnaFdQOWZVTGpjZmFhblJCN0N4WFR6QlkiLCJtYWMiOiJlZDAzNjZhYmM2YThlYjMxZmVjNmYyZjkxZmQ2OWJkYzFlYTc0ZDNlZjk3YzVjNWUyNDJmN2Q0YTYzMzI4OTcyIiwidGFnIjoiIn0%3D; 591_new_session=eyJpdiI6Ik1HM2VkdjlocFpiSHkvWWY2RGVUN1E9PSIsInZhbHVlIjoiallvaDJKWWZxZGlhSE9BSTFyTksxdXNRYnovaUVZSmxGYzlJTEIwUjZqeGV1V2RTZ2xwTHpiTmxKY1EyMU81WmFkTjdqT1pDN2pJNW11Sjk3dDhiN2VDT2RHb1YzM3lteGpra0tqMlFaaVlWNlM2VDlJR3diTVB2NmNFR1V0czYiLCJtYWMiOiI0OTM5OGZjMzI0YjE2ZTA1NzRiYWFhNzczMTAxY2FmYzkzNDFmYzczZDM0OGJlZGFhNjM2YmEzNGM1Mjc3M2MyIiwidGFnIjoiIn0%3D',
        'Device': 'pc',
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
        'X-Csrf-Token': 'sZxjNF8qKk2hlkDnkt6XKDNwA1Nz6q9a6AM3gJpZ',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.get(url, params=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def process_and_insert_data():
    rental_data = fetch_rental_data()
    print(rental_data)
    if rental_data is None:
        return


if __name__ == '__main__':
    process_and_insert_data()
