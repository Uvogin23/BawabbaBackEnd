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
    cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        user_id, db_username, db_password, role = user

        # Check if the password matches
        if bcrypt.check_password_hash(db_password, password):
            # Generate access token
            access_token = create_access_token(identity={"id": user_id, "username": db_username, "role": role})

            # Return user's info along with the token (password excluded)
            return jsonify({
                "access_token": access_token,
                "user": {
                    "id": user_id,
                    "username": db_username,
                    "role": role
                }
            })

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

@login_bp.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.json

    # Extract user data
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # Extract employee data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    grade = data.get('grade')
    badge_number = data.get('badge_number')

    if not (username and password and role and first_name and last_name and grade and badge_number):
        return jsonify({"msg": "All fields are required!"}), 400

    try:
        cursor = mysql.connection.cursor()

        # Check if username already exists
        check_user_query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(check_user_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"msg": "Username already exists!"}), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user data into users table
        user_query = """
            INSERT INTO users (username, password, role) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(user_query, (username, hashed_password, role))
        user_id = cursor.lastrowid  # Get the inserted user's ID

        # Insert employee data into employee table
        employee_query = """
            INSERT INTO employee (user_id, first_name, last_name, grade, badge_number) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(employee_query, (user_id, first_name, last_name, grade, badge_number))

        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Employee added successfully!"}), 201

    except Exception as e:
        # Rollback in case of an error
        mysql.connection.rollback()
        return jsonify({"msg": "Error adding employee!", "error": str(e)}), 500

@login_bp.route('/get_all_users_employees', methods=['GET'])
def get_all_users_employees():
    try:
        cursor = mysql.connection.cursor()

        # SQL query to join users and employees
        query = """
        SELECT 
            users.id AS user_id,
            users.username,
            users.role,
            employee.id AS employee_id,
            employee.first_name,
            employee.last_name,
            employee.grade,
            employee.badge_number
        FROM 
            users
        LEFT JOIN 
            employee ON users.id = employee.user_id
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Prepare the response
        users_employees = []
        for row in results:
            users_employees.append({
                "user_id": row[0],
                "username": row[1],
                "role": row[2],
                "employee_id": row[3],
                "first_name": row[4],
                "last_name": row[5],
                "grade": row[6],
                "badge_number": row[7]
            })

        cursor.close()
        return jsonify(users_employees)

    except Exception as e:
        return jsonify({"msg": "Error fetching users and employees!", "error": str(e)}), 500

@login_bp.route('/update_employee/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json
    
    # Create a list to store the fields we want to update
    update_fields = []
    query_values = []
    
    # Check if the username, role, rank, or password is provided and add to the update query
    if 'role' in data:
        update_fields.append("role = %s")
        query_values.append(data['role'])

    if 'grade' in data:
        update_fields.append("grade = %s")
        query_values.append(data['grade'])

    if 'password' in data:
        # Hash the password before updating
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        update_fields.append("password = %s")
        query_values.append(hashed_password)

    # Ensure there are fields to update
    if not update_fields:
        return jsonify({"msg": "No fields to update!"}), 400
    
    # Add employee_id to the query values for the WHERE clause
    query_values.append(employee_id)

    # Create the update query string dynamically based on provided fields
    update_query = f"""
        UPDATE users u
        JOIN employee e ON u.id = e.user_id
        SET {', '.join(update_fields)}
        WHERE e.id = %s
    """

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(update_query, tuple(query_values))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"msg": "Employee not found!"}), 404

        cursor.close()

        return jsonify({"msg": "Employee updated successfully!"}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error updating employee!", "error": str(e)}), 500

@login_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor = mysql.connection.cursor()

        # Delete the user directly (employee will be deleted automatically due to cascading)
        delete_user_query = """
            DELETE FROM users WHERE id = %s
        """
        cursor.execute(delete_user_query, (user_id,))

        # If no user is deleted, it means the user was not found
        if cursor.rowcount == 0:
            return jsonify({"msg": "User not found!"}), 404

        # Commit the changes
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "User and associated employee deleted successfully!"}), 200

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error deleting user!", "error": str(e)}), 500