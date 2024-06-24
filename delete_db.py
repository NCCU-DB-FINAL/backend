'''
不要亂run，不然可能會被討厭
'''
import mysql.connector
from mysql.connector import Error
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
            password=os.getenv('DB_PASSWORD')
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection

def drop_database(connection):
    """刪除資料庫"""
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS rental_db")
    connection.commit()
    cursor.close()
    print("Database 'rental_db' has been dropped")

if __name__ == "__main__":
    connection = create_connection()
    if connection:
        drop_database(connection)
        connection.close()
