from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from flask import Blueprint, jsonify


citizens_bp = Blueprint('citizens', __name__)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

# Retrieve all citizens
@citizens_bp.route('/api/citizens', methods=['GET'])
def get_all_citizens():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM citizens")
        results = cur.fetchall()
        cur.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Retrieve a single citizen by ID
@citizens_bp.route('/api/citizens/<int:id>', methods=['GET'])
def get_citizen(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM citizens WHERE id = %s", (id,))
        citizen = cur.fetchone()
        cur.close()

        if citizen:
            citizen_data = {
                'id': citizen[0],
                'first_name': citizen[1],
                'last_name': citizen[2],
                'date_of_birth': citizen[3],
                'place_of_birth': citizen[4],
                'passport_number': citizen[5],
                'passport_expiry': citizen[6],
                'fonction': citizen[7],
                'exit_date': citizen[8],
                'entry_date': citizen[9],
                'message_reference': citizen[10],
                'address': citizen[11],
                'vehicle_type': citizen[12],
                'plate_number': citizen[13],
                'observations': citizen[14],
                'created_at': citizen[15],
                'msg_ref': citizen[16]
            }
            return jsonify(citizen_data), 200
        else:
            return jsonify({'message': 'Citizen not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a new citizen
@citizens_bp.route('/api/citizens/add', methods=['POST'])
def add_citizen():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO citizens (
                first_name, last_name, date_of_birth, place_of_birth, passport_number,
                passport_expiry, fonction, exit_date, entry_date, message_reference,
                address, vehicle_type, plate_number, observations, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data.get('place_of_birth'),
            data['passport_number'], data.get('passport_expiry'), data.get('fonction'), data['exit_date'],
            data.get('entry_date'), data.get('message_reference'), data.get('address'), data.get('vehicle_type'),
            data.get('plate_number'), data.get('observations'), data.get('msg_ref')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Citizen added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add citizen'}), 500

# Update a citizen by ID
@citizens_bp.route('/api/citizens/Update/<int:id>', methods=['PUT'])
def update_citizen(id):
    data = request.json
    try:
        update_fields = []
        values = []

        # Add each field if present in request
        for field in ['passport_expiry', 'fonction', 'entry_date', 'message_reference', 'address', 'vehicle_type', 'plate_number', 'observations', 'msg_ref']:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            return jsonify({"error": "No fields provided for update"}), 400

        query = f"UPDATE citizens SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Citizen updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a citizen by ID
@citizens_bp.route('/api/citizens/Delete/<int:id>', methods=['DELETE'])
def delete_citizen(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM citizens WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Citizen deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get monthly counts of citizens based on exit date
@citizens_bp.route('/api/citizens/monthly-counts', methods=['GET'])
def get_citizens_monthly_counts():
    try:
        year = request.args.get('year')

        if not year or not year.isdigit() or int(year) < 1900 or int(year) > datetime.now().year:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        query = """
            SELECT MONTH(exit_date) AS month, COUNT(*) AS count
            FROM citizens
            WHERE YEAR(exit_date) = %s
            GROUP BY month
            ORDER BY month
        """

        cur = mysql.connection.cursor()
        cur.execute(query, (year,))
        results = cur.fetchall()
        cur.close()

        monthly_counts = {i: 0 for i in range(1, 13)}
        total_count = 0

        for row in results:
            month = row[0]
            count = row[1]
            monthly_counts[month] = count
            total_count += count

        response_data = {
            "year": year,
            "monthly_counts": monthly_counts,
            "total_count": total_count
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Filter citizens by specific criteria
@citizens_bp.route('/api/citizens/filter', methods=['GET'])
def filter_citizens():
    try:
        cur = mysql.connection.cursor()
        
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        place_of_birth = request.args.get('place_of_birth')
        passport_number = request.args.get('passport_number')
        fonction = request.args.get('fonction')
        msg_ref = request.args.get('msg_ref')
        entry_date_start = request.args.get('entry_date_start')
        entry_date_end = request.args.get('entry_date_end')

        query = "SELECT * FROM citizens WHERE 1=1"
        filters = []

        if first_name:
            query += " AND first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND last_name = %s"
            filters.append(last_name)

        if place_of_birth:
            query += " AND place_of_birth = %s"
            filters.append(place_of_birth)

        if passport_number:
            query += " AND passport_number = %s"
            filters.append(passport_number)

        if fonction:
            query += " AND fonction = %s"
            filters.append(fonction)

        if msg_ref:
            query += " AND msg_ref = %s"
            filters.append(msg_ref)

        if entry_date_start and entry_date_end:
            try:
                entry_date_start = datetime.strptime(entry_date_start, '%Y-%m-%d').date()
                entry_date_end = datetime.strptime(entry_date_end, '%Y-%m-%d').date()
                query += " AND entry_date BETWEEN %s AND %s"
                filters.extend([entry_date_start, entry_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        cur.execute(query, tuple(filters))
        results = cur.fetchall()

        if not results:
            return jsonify({"message": "No citizens found matching the criteria"}), 404

        column_names = [desc[0] for desc in cur.description]
        citizens = [dict(zip(column_names, row)) for row in results]
        total_count = len(citizens)
        fonction_counts = Counter(citizen['fonction'] for citizen in citizens)

        cur.close()

        response_data = {
            "total_citizens": total_count,
            "fonction_counts": dict(fonction_counts),
            "citizens": citizens
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

