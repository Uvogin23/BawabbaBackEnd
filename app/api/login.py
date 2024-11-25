from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

login_bp = Blueprint('login', __name__)
app = Flask(__name__)
CORS(app)

# Configurations
app.config['JWT_SECRET_KEY'] = 'e6a8b42d4e3e5d96f9c4b0d8a7f12c4e9d87c0a62b8a9d1d6e7c8f9b8a1c2d3e'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mysql = MySQL(app)

# User Login Endpoint
@login_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required!"}), 400

    # Query the database for the user
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        db_username, db_password, role = user

        # Check if the password matches
        if bcrypt.check_password_hash(db_password, password):
            # Generate access token
            access_token = create_access_token(identity={"username": db_username, "role": role})
            return jsonify(access_token=access_token)

    return jsonify({"msg": "Invalid username or password!"}), 401

# Protected Endpoint
@login_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

# Role-Based Endpoint (Example)
@login_bp.route('/admin-only', methods=['GET'])
@jwt_required()
def admin_only():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"msg": "Admins only!"}), 403
    return jsonify({"msg": "Welcome, admin!"})

# User Registration Endpoint (Optional)
@login_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')

    if not username or not password or not role:
        return jsonify({"msg": "All fields are required!"}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert user into the database
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, hashed_password, role))
        mysql.connection.commit()
        return jsonify({"msg": "User registered successfully!"}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error occurred while registering the user!", "error": str(e)}), 500
    finally:
        cursor.close()





