import hashlib
from datetime import datetime, timedelta

import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = 'NCCUSQL'
# app.config['JWT_SECRET_KEY'] = secrets.token_hex(32) 隨機密鑰
jwt = JWTManager(app)


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

    # 檢查用戶名稱是否存在
    if user_type == 'landlord':
        cursor.execute("SELECT * FROM LandLord WHERE L_Name = %s", (username,))
    elif user_type == 'tenant':
        cursor.execute("SELECT * FROM Tenant WHERE T_Name = %s", (username,))

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Username already exists'}), 409

    # 插入新用戶
    try:
        if user_type == 'landlord':
            cursor.execute("INSERT INTO LandLord (L_Name, L_PhoneNum, Password) VALUES (%s, %s, %s)",
                           (username, phonenum, hashed_password))
        elif user_type == 'tenant':
            cursor.execute("INSERT INTO Tenant (T_Name, T_PhoneNum, Password) VALUES (%s, %s, %s)",
                           (username, phonenum, hashed_password))
        connection.commit()
    except Error as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'message': f'Error: {e}'}), 500

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
        # JWT
        access_token = create_access_token(identity={'user_id': user_data[0], 'user_type': user_type},
                                           expires_delta=timedelta(days=1))
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


@app.route('/api/rental/<int:id>', methods=['PUT'])
@jwt_required()
def update_rental(id):
    """房東修改租屋資訊"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'landlord':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    address = data.get('address')
    title = data.get('title')
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
        "UPDATE Rental SET Address=%s, Title=%s, Price=%s, Type=%s, Bedroom=%s, LivingRoom=%s, Bathroom=%s, Ping=%s, RentalTerm=%s WHERE R_id=%s AND L_id=%s",
        (address, title, price, type, bedroom, living_room, bathroom, ping, rental_term, id, current_user['user_id']))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental updated successfully!'}), 200


@app.route('/api/rental/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_rental(id):
    """房東刪除租屋資訊"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'landlord':
        return jsonify({'message': 'Unauthorized'}), 403

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Rental WHERE R_id=%s AND L_id=%s", (id, current_user['user_id']))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental deleted successfully!'}), 200


@app.route('/api/rental', methods=['POST'])
@jwt_required()
def add_rental():
    """房東新增租屋資訊"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'landlord':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    address = data.get('address')
    title = data.get('title')
    price = data.get('price')
    type = data.get('type')
    bedroom = data.get('bedroom')
    living_room = data.get('living_room')
    bathroom = data.get('bathroom')
    ping = data.get('ping')
    rental_term = data.get('rental_term')
    post_date = datetime.now().strftime('%Y-%m-%d')

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Rental (Address, Title, Price, Type, Bedroom, LivingRoom, Bathroom, Ping, RentalTerm, PostDate, L_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (address, title, price, type, bedroom, living_room, bathroom, ping, rental_term, post_date, current_user['user_id']))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental added successfully!'}), 201


@app.route('/api/rental', methods=['GET'])
@jwt_required()
def get_user_rentals():
    """房東查看自己貼的所有租屋資訊"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'landlord':
        return jsonify({'message': 'Unauthorized'}), 403

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Rental WHERE L_id = %s", (current_user['user_id'],))
    rentals = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify({'rentals': rentals}), 200


@app.route('/api/rental/search', methods=['GET'])
def search_rental():
    """房客搜尋租屋資訊"""
    search_criteria = request.args
    area = search_criteria.get('area')
    min_price = search_criteria.get('min_price', type=int)
    max_price = search_criteria.get('max_price', type=int)
    min_ping = search_criteria.get('min_ping', type=int)
    max_ping = search_criteria.get('max_ping', type=int)
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
    cursor = connection.cursor(dictionary=True)
    
    # 查詢租屋資訊
    cursor.execute(
        "SELECT Rental.*, LandLord.L_Name, LandLord.L_PhoneNum FROM Rental LEFT JOIN LandLord ON Rental.L_id = LandLord.L_id WHERE R_id=%s", 
        (id,)
    )
    rental = cursor.fetchone()
    
    if not rental:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Rental not found!'}), 404
    
    # 查詢評論
    cursor.execute(
        "SELECT Timestamp, Rating, Comment FROM Review WHERE R_id=%s", 
        (id,)
    )
    reviews = cursor.fetchall()
    
    cursor.close()
    connection.close()

    # 構建返回結果
    response = {
        "R_id": rental["R_id"],
        "Address": rental["Address"],
        "Title": rental["Title"],
        "Price": rental["Price"],
        "Type": rental["Type"],
        "Bedroom": rental["Bedroom"],
        "LivingRoom": rental["LivingRoom"],
        "Bathroom": rental["Bathroom"],
        "Ping": rental["Ping"],
        "RentalTerm": rental["RentalTerm"],
        "PostDate": rental["PostDate"],
        "L_Name": rental["L_Name"],
        "L_PhoneNum": rental["L_PhoneNum"],
        "Reviews": reviews
    }
    
    return jsonify(response), 200


@app.route('/api/like', methods=['POST'])
@jwt_required()
def like_rental():
    """房客收藏喜歡的房子"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'tenant':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    rental_id = data.get('rental_id')

    tenant_id = current_user['user_id']
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # 檢查是否已經收藏過
        cursor.execute("SELECT * FROM Favorite WHERE R_id = %s AND T_id = %s", (rental_id, tenant_id))
        existing_favorite = cursor.fetchone()

        if existing_favorite:
            cursor.close()
            connection.close()
            return jsonify({'message': 'Rental already liked'}), 409

        # 插入新的收藏紀錄
        cursor.execute("INSERT INTO Favorite (R_id, T_id) VALUES (%s, %s)", (rental_id, tenant_id))
        connection.commit()
    except Error as e:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'message': f'Error: {str(e)}'}), 500

    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental liked successfully!'}), 201



@app.route('/api/like', methods=['DELETE'])
@jwt_required()
def unlike_rental():
    """房客取消收藏喜歡的房子"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'tenant':
        return jsonify({'message': 'Unauthorized'}), 403
    data = request.get_json()
    rental_id = data.get('rental_id')

    tenant_id = current_user['user_id']
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Favorite WHERE R_id = %s AND T_id = %s", (rental_id, tenant_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Rental unliked successfully!'}), 200


@app.route('/api/comment/<int:id>', methods=['POST'])
@jwt_required()
def add_comment(id):
    """房客對租屋資訊留下評論"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'tenant':
        return jsonify({'message': 'Unauthorized'}), 403

    tenant_id = current_user['user_id']
    data = request.get_json()
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
@jwt_required()
def view_likes():
    """房客查看收藏清單"""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'tenant':
        return jsonify({'message': 'Unauthorized'}), 403

    tenant_id = current_user['user_id']
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
    SELECT r.R_id, r.Address, r.Title, r.Price, r.Type, r.Bedroom, r.LivingRoom, r.Bathroom, r.Ping, r.RentalTerm, r.PostDate
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
