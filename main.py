from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def create_connection():
    """建立連接"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host='mysql-nccu.mysql.database.azure.com',
            user='nccu',
            password='123!@#qaz',
            database='rental_db'
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection


def hash_password(password):
    """密碼雜湊函數"""
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/api/signup', methods=['POST'])
def signup():
    """註冊房東或房客"""
    data = request.get_json()
    username = data.get('username')
    phonenum = data.get('phonenum')
    password = data.get('password')
    hashed_password = hash_password(password)
    user_type = data.get('type')

    connection = create_connection()
    cursor = connection.cursor()

    if user_type == 'landlord':
        cursor.execute("INSERT INTO LandLord (L_Name, L_PhoneNum, Password) VALUES (%s, %s, %s)",
                       (username, phonenum, hashed_password))
    elif user_type == 'tenant':
        cursor.execute("INSERT INTO Tenant (T_Name, L_PhoneNum, Password) VALUES (%s, %s, %s)",
                       (username, phonenum, hashed_password))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    """登入房東或房客"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_password = hash_password(password)
    user_type = data.get('type')

    connection = create_connection()
    cursor = connection.cursor()

    if user_type == 'landlord':
        cursor.execute("SELECT L_id, Password FROM LandLord WHERE L_Name = %s", (username,))
    elif user_type == 'tenant':
        cursor.execute("SELECT T_id, Password FROM Tenant WHERE T_Name = %s", (username,))

    user_data = cursor.fetchone()
    cursor.close()
    connection.close()

    if user_data and user_data[1] == hashed_password:
        return jsonify({'user_id': user_data[0]}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/api/rental', methods=['POST'])
def add_rental():
    """房東新增租屋資訊"""
    data = request.get_json()
    address = data.get('address')
    price = data.get('price')
    type = data.get('type')
    bedroom = data.get('bedroom')
    living_room = data.get('living_room')
    bathroom = data.get('bathroom')
    ping = data.get('ping')
    rental_term = data.get('rental_term')
    post_date = datetime.now().strftime('%Y-%m-%d')
    landLord_id = data.get('landLord_id')

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Rental (Address, Price, Type, Bedroom, LivingRoom, Bathroom, Ping, RentalTerm, PostDate, L_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (address, price, type, bedroom, living_room, bathroom, ping, rental_term, post_date, landLord_id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental added successfully!'}), 201


@app.route('/api/rental/<int:id>', methods=['PUT'])
def update_rental(id):
    """房東修改租屋資訊"""
    data = request.get_json()
    address = data.get('address')
    price = data.get('price')
    type = data.get('type')
    bedroom = data.get('bedroom')
    living_room = data.get('living_room')
    bathroom = data.get('bathroom')
    ping = data.get('ping')
    rental_term = data.get('rental_term')

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Rental SET Address=%s, Price=%s, Type=%s, Bedroom=%s, LivingRoom=%s, Bathroom=%s, Ping=%s, RentalTerm=%s WHERE R_id=%s",
        (address, price, type, bedroom, living_room, bathroom, ping, rental_term, id))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental updated successfully!'}), 200


@app.route('/api/rental/<int:id>', methods=['DELETE'])
def delete_rental(id):
    """房東刪除租屋資訊"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Rental WHERE R_id=%s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental deleted successfully!'}), 200

@app.route('/api/rental', methods=['GET'])
def get_user_rentals():
    """房東查看自己貼的所有租屋資訊"""
    user_id = request.args.get('user')
    
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Rental WHERE L_id = %s", (user_id,))
    rentals = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return jsonify({'rentals': rentals}), 200
    
@app.route('/api/rental/search', methods=['GET'])
def search_rental():
    """房客搜尋租屋資訊"""
    search_criteria = request.get_json()

    area = search_criteria.get('area')
    min_price = search_criteria.get('min_price')
    max_price = search_criteria.get('max_price')
    min_ping = search_criteria.get('min_ping')
    max_ping = search_criteria.get('max_ping')
    sort_by = search_criteria.get('sort_by')

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM Rental WHERE 1=1"
    if area:
        query += f" AND Address LIKE '%{area}%'"
    if min_price:
        query += f" AND Price >= {min_price}"
    if max_price:
        query += f" AND Price <= {max_price}"
    if min_ping:
        query += f" AND Ping >= {min_ping}"
    if max_ping:
        query += f" AND Ping <= {max_ping}"
    if sort_by:
        query += f" ORDER BY {sort_by}"

    cursor.execute(query)
    search_results = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify({'rentals': search_results}), 200

@app.route('/api/rental/<int:id>', methods=['GET'])
def get_rental(id):
    """房客瀏覽單獨物件資訊"""
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM Rental WHERE R_id=%s", (id))
    rental = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if not rental:
        return jsonify({'message': 'Rental not found!'}), 404
    return jsonify({'rental': rental}), 200
    
@app.route('/api/like/<int:id>', methods=['POST'])
def like_rental(id):
    """房客收藏喜歡的房子"""
    data = request.get_json()
    tenant_id = data.get('tenant_id')

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Favorite (R_id, T_id) VALUES (%s, %s)", (id, tenant_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental liked successfully!'}), 201

@app.route('/api/like/<int:id>', methods=['DELETE'])
def unlike_rental(id):
    """房客刪除收藏喜歡的房子"""
    data = request.get_json()
    tenant_id = data.get('tenant_id')

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Favorite WHERE R_id = %s AND T_id = %s", (id, tenant_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental unliked successfully!'}), 200

@app.route('/api/comment/<int:id>', methods=['POST'])
def add_comment(id):
    """房客對租屋資訊留下評論"""
    data = request.get_json()
    tenant_id = data.get('tenant_id')  # 假設前端將房客ID傳遞過來
    rating = data.get('rating')
    comment = data.get('comment')

    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO Review (T_id, R_id, Rating, Comment) VALUES (%s, %s, %s, %s)",
                   (tenant_id, id, rating, comment))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Comment added successfully!'}), 201

@app.route('/api/likes', methods=['GET'])
def view_likes():
    """房客查看收藏清單"""
    tenant_id = request.args.get('tenant_id')

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT r.R_id, r.Address, r.Price, r.Type, r.Bedroom, r.LivingRoom, r.Bathroom, r.Ping, r.RentalTerm, r.PostDate
    FROM Favorite f
    JOIN Rental r ON f.R_id = r.R_id
    WHERE f.T_id = %s
    """
    cursor.execute(query, (tenant_id,))
    liked_rentals = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return jsonify({'liked_rentals': liked_rentals}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
