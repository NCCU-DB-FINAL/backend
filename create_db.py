import mysql.connector
from mysql.connector import Error

def create_connection():
    """建立連接"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host='mysql.h9bxbshbg9f4bjb9.japaneast.azurecontainer.io',
            user='root',
            password='nccunccunccu',
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection


def create_database(connection):
    """創建資料庫"""
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS rental_db")
    cursor.execute("CREATE DATABASE rental_db")
    connection.commit()
    cursor.close()
    print("Database 'rental_db' created successfully")


def create_tables(connection):
    """創建資料表"""
    cursor = connection.cursor()
    cursor.execute("USE rental_db")

    # LandLord
    cursor.execute("""
        CREATE TABLE LandLord (
            L_id INT AUTO_INCREMENT PRIMARY KEY,
            L_Name VARCHAR(100) NOT NULL,
            L_PhoneNum VARCHAR(15) NOT NULL,
            Password VARCHAR(300) NOT NULL
        )
    """)

    # Tenant
    cursor.execute("""
        CREATE TABLE Tenant (
            T_id INT AUTO_INCREMENT PRIMARY KEY,
            T_Name VARCHAR(100) NOT NULL,
            T_PhoneNum VARCHAR(15) NOT NULL,
            Password VARCHAR(300) NOT NULL
        )
    """)

    # Rental
    cursor.execute("""
        CREATE TABLE Rental (
            R_id INT AUTO_INCREMENT PRIMARY KEY,
            Address VARCHAR(255) NOT NULL,
            Price DECIMAL(10, 2) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Bedroom INT NOT NULL,
            LivingRoom INT NOT NULL,
            Bathroom INT NOT NULL,
            Ping DECIMAL(5, 2) NOT NULL,
            RentalTerm VARCHAR(50) NOT NULL,
            PostDate DATE NOT NULL,
            L_id INT NOT NULL,
            FOREIGN KEY (L_id) REFERENCES LandLord(L_id)
        )
    """)

    # Favorite
    cursor.execute("""
        CREATE TABLE Favorite (
            R_id INT NOT NULL,
            T_id INT NOT NULL,
            PRIMARY KEY (R_id, T_id),
            FOREIGN KEY (R_id) REFERENCES Rental(R_id),
            FOREIGN KEY (T_id) REFERENCES Tenant(T_id)
        )
    """)

    # Review
    cursor.execute("""
        CREATE TABLE Review (
            Review_id INT AUTO_INCREMENT PRIMARY KEY,
            Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            T_id INT NOT NULL,
            R_id INT NOT NULL,
            Rating INT NOT NULL,
            Comment TEXT NOT NULL,
            FOREIGN KEY (T_id) REFERENCES Tenant(T_id),
            FOREIGN KEY (R_id) REFERENCES Rental(R_id)
        )
    """)

    connection.commit()
    cursor.close()
    print("Tables created successfully")


if __name__ == "__main__":
    connection = create_connection()
    if connection:
        create_database(connection)
        create_tables(connection)
        connection.close()
