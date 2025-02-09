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
        cursor = mysql.connection.cursor()
        query = """
        SELECT 
        c.*, 
        cdl.dep_msg_ref,
        cdl.departure_time   
        FROM 
        citizens c
        LEFT JOIN 
        citizen_departure_logs cdl 
        ON 
        c.id = cdl. citizen_id;
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching citizens ", "error": str(e)}), 500
    
@citizens_bp.route('/api/citizens/still_out', methods=['GET'])
def get_citizens_stillOut():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
            c.*,
            cdl.dep_msg_ref,
            cdl.departure_time  
        FROM 
            citizens c
        LEFT JOIN 
            citizen_departure_logs cdl
        ON 
            c.id = cdl.citizen_id
        WHERE 
            cdl.citizen_id IS NULL
        AND 
        c.exit_date > DATE_SUB(CURDATE(), INTERVAL 2 MONTH);
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching citizens still in the city", "error": str(e)}), 500

@citizens_bp.route('/api/citizens/supposedToEnter', methods=['GET'])
def get_citizens_supposedToEnter():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        c.*, 
        cdl.dep_msg_ref,
        cdl.departure_time 
        FROM 
        citizens c
        LEFT JOIN 
        citizen_departure_logs cdl 
        ON 
        c.id = cdl.citizen_id
        WHERE 
        cdl.citizen_id IS NULL
        AND 
        c.exit_date <= DATE_SUB(CURDATE(), INTERVAL 2 MONTH);
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching citizens out for two months or more", "error": str(e)}), 500

@citizens_bp.route('/api/citizens/history', methods=['GET'])
def get_citizens_history():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        c.*,
        cdl.dep_msg_ref,
        cdl.departure_time   
        FROM 
        citizens c
        INNER JOIN 
        citizen_departure_logs cdl 
        ON 
        c.id = cdl.citizen_id
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching non_residents ", "error": str(e)}), 500

# Add a new citizen
@citizens_bp.route('/api/citizens/add', methods=['POST'])
def add_citizen():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO citizens (
                first_name, last_name, date_of_birth, place_of_birth, passport_number,
                passport_expiry, fonction, exit_date, 
                address, vehicle_type, plate_number, observations, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,  %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data.get('place_of_birth'),
            data['passport_number'], data.get('passport_expiry'), data.get('fonction'), data['exit_date'],
            data.get('address'), data.get('vehicle_type'),
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
        # Initialize query and list for fields to update
        update_fields = []
        values = []

        # Check each field, and only add it to the query if it exists in the request data
        if 'fonction' in data:
            update_fields.append("fonction = %s")
            values.append(data['fonction'])

        if 'address' in data:
            update_fields.append("address = %s")
            values.append(data['address'])

        if 'observations' in data:
            # Fetch the current value of observations
            cur = mysql.connection.cursor()
            cur.execute("SELECT observations FROM citizens WHERE id = %s", (id,))
            current_observations = cur.fetchone()
            cur.close()

            # Append the new observations to the existing ones
            if current_observations and current_observations[0]:
                updated_observations = current_observations[0] + " " + data['observations']
            else:
                updated_observations = data['observations']

            update_fields.append("observations = %s")
            values.append(updated_observations)

        if 'msg_ref' in data:
            update_fields.append("msg_ref = %s")
            values.append(data['msg_ref'])

        # If no fields are provided, return an error response
        if not update_fields:
            return jsonify({"error": "No fields provided for update"}), 400

        # Join the fields with commas and add to the SQL statement
        query = f"UPDATE citizens SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)  # Add the ID to the values list for the WHERE clause

        # Execute the query with the dynamic list of values
        cur = mysql.connection.cursor()
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'citizens updated successfully!'}), 200

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

        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 2023 or int(year) > datetime.now().year + 1:
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

        # Initialize the response structure for "Algerie"
        monthly_counts = {m: 0 for m in range(1, 13)}  # Default all months to 0
        grand_total = 0

        # Process the results
        for row in results:
            month, count = row
            monthly_counts[month] = count
            grand_total += count

        # Prepare the response data
        response_data = {
            "countries": [
                {
                    "nationality": "Algerie",
                    "monthly_counts": [monthly_counts[month] for month in range(1, 13)],
                    "total": grand_total
                }
            ],
            "grand_total": grand_total
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Filter citizens by specific criteria
@citizens_bp.route('/api/citizens/filter', methods=['POST'])
def filter_citizens():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract filter parameters
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        exit_date_start = data.get('exit_date_start')
        exit_date_end = data.get('exit_date_end')
        vehicle_type = data.get('vehicle_type')
        place_of_birth = data.get('place_of_birth')
        passport_number = data.get('passport_number')
        msg_ref = data.get('msg_ref')

        # Initialize SQL query
        query = """
            SELECT 
                c.*,
                cdl.dep_msg_ref,
                cdl.departure_time
            FROM 
                citizens c
            LEFT JOIN 
                citizen_departure_logs cdl
            ON 
                c.id = cdl.citizen_id
            WHERE 1=1
        """
        filters = []

        # Add filters to the query
        if first_name:
            query += " AND c.first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND c.last_name = %s"
            filters.append(last_name)

        if place_of_birth:
            query += " AND c.place_of_birth = %s"
            filters.append(place_of_birth)

        if exit_date_start and exit_date_end:
            try:
                exit_date_start = datetime.strptime(exit_date_start, '%Y-%m-%d').date()
                exit_date_end = datetime.strptime(exit_date_end, '%Y-%m-%d').date()
                query += " AND c.exit_date BETWEEN %s AND %s"
                filters.extend([exit_date_start, exit_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if vehicle_type:
            query += " AND c.vehicle_type LIKE %s"
            filters.append(vehicle_type)

        if passport_number:
            query += " AND c.passport_number LIKE %s"
            filters.append(f"%{passport_number}%")

        if msg_ref:
            query += " AND c.msg_ref = %s"
            filters.append(msg_ref)

        # Execute the query
        cur = mysql.connection.cursor()
        cur.execute(query, tuple(filters))
        results = cur.fetchall()

        # Transform the results into a nested list
        results_list = [list(row) for row in results]

        cur.close()
        return jsonify(results_list), 200  # Return the nested list

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@citizens_bp.route('/api/citizens/last-two', methods=['GET'])
def get_last_two_non_residents():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = """
        SELECT 
    c.*,
    cdl.dep_msg_ref,
    cdl.departure_time   
FROM 
    citizens c
LEFT JOIN 
    citizen_departure_logs cdl 
ON 
    c.id = cdl.citizen_id
ORDER BY 
    c.id DESC
LIMIT 2;
        """
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@citizens_bp.route('/api/citizens/add_departure_log', methods=['POST'])
def add_departure_log():
    data = request.json
    
    # Extract values from the request
    citizen_id = data.get('citizen_id')
    departure_method = data.get('observations')
    departure_time = data.get('departure_time')
    dep_msg_ref = data.get('dep_msg_ref')

    # Ensure all required fields are provided
    if not citizen_id :
        return jsonify({"msg": "citizen_id  is required!"}), 400
    
    if not departure_method:
         return jsonify({"msg": " departure_method is required!"}), 400

    if not departure_time:
         return jsonify({"msg": "departure_time is required!"}), 400
    
    try:
        cursor = mysql.connection.cursor()
        
        # Insert data into non_resident_departure_logs table
        insert_query = """
            INSERT INTO citizen_departure_logs (citizen_id, departure_method, departure_time, dep_msg_ref)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (citizen_id, departure_method, departure_time, dep_msg_ref))
        
        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Departure log added successfully!"}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error adding departure log!", "error": str(e)}), 500