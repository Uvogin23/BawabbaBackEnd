from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from flask import Blueprint, jsonify

diplomats_bp = Blueprint('diplomats', __name__)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

# Retrieve all diplomats
@diplomats_bp.route('/api/diplomats', methods=['GET'])
def get_data():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        d.*, 
        ddl.dep_msg_ref  
        FROM 
        diplomats d
        LEFT JOIN 
        diplomat_departure_logs ddl 
        ON 
        d.id = ddl.diplomat_id;
        """
        cursor.execute(query)
        diplomats = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in diplomats]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching diplomats ", "error": str(e)}), 500

@diplomats_bp.route('/api/diplomats/still_in_city', methods=['GET'])
def get_diplomats_still_in_city():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
    d.*,
    ddl.dep_msg_ref  
FROM 
    diplomats d
LEFT JOIN 
    diplomat_departure_logs ddl
ON 
    d.id = ddl.diplomat_id
WHERE 
    ddl.diplomat_id IS NULL
    AND d.expected_departure_date > CURDATE();
        """
        cursor.execute(query)
        diplomats = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in diplomats]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching diplomats", "error": str(e)}), 500

@diplomats_bp.route('/api/diplomats/supposed_to_leave', methods=['GET'])
def get_diplomats_supposed_to_leave():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
    d.*,
    ddl.dep_msg_ref  
FROM 
    diplomats d
LEFT JOIN 
    diplomat_departure_logs ddl 
ON 
    d.id = ddl.diplomat_id
WHERE 
    ddl.diplomat_id IS NULL
    AND (d.expected_departure_date <= CURDATE());
        """
        cursor.execute(query)
        diplomats = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in diplomats]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists still in the city", "error": str(e)}), 500

@diplomats_bp.route('/api/diplomats/history', methods=['GET'])
def get_diplomats_history():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        d.*,
        ddl.dep_msg_ref  
        FROM 
        diplomats d
        INNER JOIN 
        diplomat_departure_logs ddl 
        ON 
        d.id = ddl.diplomat_id;
        """
        cursor.execute(query)
        diplomats = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in diplomats]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching diplomats ", "error": str(e)}), 500

# Retrieve a single diplomat by ID
@diplomats_bp.route('/api/diplomats/last', methods=['GET'])
def get_last_diplomat_id():
    try:
        # Query to get the last inserted diplomat's ID
        query = """
            SELECT id 
            FROM diplomats 
            ORDER BY id DESC 
            LIMIT 1
        """

        cur = mysql.connection.cursor()
        cur.execute(query)
        result = cur.fetchone()
        cur.close()

        if result:
            # If a result is found, return the ID
            last_id = result[0]
            return jsonify({"last_id": last_id}), 200
        else:
            # If no diplomats exist in the table
            return jsonify({"message": "No diplomats found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a single diplomat
@diplomats_bp.route('/api/diplomats/add', methods=['POST'])
def add_diplomat():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO diplomats (
                first_name, last_name, date_of_birth, place_of_birth, passport_number, passport_expiry,
                diplomatic_card_number, fonction, nationality, receiving_agency, circuit, arrival_date,
                expected_departure_date, arrival_flight_info, departure_flight_info, touristic_guide, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data['place_of_birth'],
            data['passport_number'], data['passport_expiry'], data['diplomatic_card_number'],
            data['fonction'], data['nationality'], data['receiving_agency'], data['circuit'],
            data['arrival_date'], data['expected_departure_date'], data['arrival_flight_info'],
            data['departure_flight_info'], data['touristic_guide'], data['msg_ref']
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Diplomat added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add diplomat'}), 500

# Delete a diplomat by ID
@diplomats_bp.route('/api/diplomats/<int:id>', methods=['DELETE'])
def delete_diplomat(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM diplomats WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Diplomat deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a diplomat by ID
@diplomats_bp.route('/api/diplomats/<int:id>', methods=['PUT'])
def update_diplomat(id):
    data = request.json
    try:
        # Initialize query and list for fields to update
        update_fields = []
        values = []

        # Check each field, and only add it to the query if it exists in the request data
        if 'receiving_agency' in data:
            update_fields.append("receiving_agency = %s")
            values.append(data['receiving_agency'])
        
        if 'circuit' in data:
            update_fields.append("circuit = %s")
            values.append(data['circuit'])
        
        if 'expected_departure_date' in data:
            update_fields.append("expected_departure_date = %s")
            values.append(data['expected_departure_date'])
        
        if 'arrival_flight_info' in data:
            update_fields.append("arrival_flight_info = %s")
            values.append(data['arrival_flight_info'])

        if 'departure_flight_info' in data:
            update_fields.append("departure_flight_info = %s")
            values.append(data['departure_flight_info'])

        if 'touristic_guide' in data:
            update_fields.append("touristic_guide = %s")
            values.append(data['touristic_guide'])
        
        if 'msg_ref' in data:
            update_fields.append("msg_ref = %s")
            values.append(data['msg_ref'])

        # If no fields are provided, return an error response
        if not update_fields:
            return jsonify({"error": "No fields provided for update"}), 400

        # Join the fields with commas and add to the SQL statement
        query = f"UPDATE diplomats SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)  # Add the ID to the values list for the WHERE clause

        # Execute the query with the dynamic list of values
        cur = mysql.connection.cursor()
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Diplomat updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Diplomats sorted by country
@diplomats_bp.route('/api/diplomats/bycountry', methods=['GET'])
def get_diplomats():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM diplomats ORDER BY nationality ASC;")
        results = cur.fetchall()

        column_names = [desc[0] for desc in cur.description]
        diplomats = [dict(zip(column_names, row)) for row in results]

        cur.close()
        return jsonify(diplomats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Number of diplomats from each country
@diplomats_bp.route('/api/diplomats/counts', methods=['GET'])
def get_diplomat_counts():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT nationality, COUNT(*) AS count
            FROM diplomats
            GROUP BY nationality
            ORDER BY count DESC;
        """)
        results = cur.fetchall()
        diplomat_counts = [{'nationality': row[0], 'count': row[1]} for row in results]

        cur.close()
        return jsonify(diplomat_counts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Show diplomat from a specific country
@diplomats_bp.route('/api/diplomats/country/<string:nationality>', methods=['GET'])
def get_diplomats_by_country(nationality):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM diplomats WHERE nationality = %s;", (nationality,))
        results = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        diplomats = [dict(zip(column_names, row)) for row in results]

        cur.close()
        return jsonify(diplomats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#flter diplomats
@diplomats_bp.route('/api/diplomats/filter', methods=['POST'])
def filter_diplomats():
    try:
        data = request.get_json()

        # Extract filter parameters
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        nationality = data.get('nationality')
        arrival_date_start = data.get('arrival_date_start')
        arrival_date_end = data.get('arrival_date_end')
        receiving_agency = data.get('receiving_agency')
        arrival_flight_info = data.get('arrival_flight_info')
        msg_ref = data.get('msg_ref')

        # Start building the SQL query
        query = """
            SELECT 
                d.*, 
                ddl.dep_msg_ref
            FROM 
                diplomats d
            LEFT JOIN 
                diplomat_departure_logs ddl
            ON 
                d.id = ddl.diplomat_id
            WHERE 1=1
        """
        filters = []

        # Add filters based on provided parameters

        if first_name:
            query += " AND d.first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND d.last_name = %s"
            filters.append(last_name)

        if nationality:
            query += " AND d.nationality = %s"
            filters.append(nationality)

        if arrival_date_start and arrival_date_end:
            try:
                arrival_date_start = datetime.strptime(arrival_date_start, '%Y-%m-%d').date()
                arrival_date_end = datetime.strptime(arrival_date_end, '%Y-%m-%d').date()
                query += " AND d.arrival_date BETWEEN %s AND %s"
                filters.extend([arrival_date_start, arrival_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if receiving_agency:
            query += " AND d.receiving_agency = %s"
            filters.append(receiving_agency)

        if arrival_flight_info:
            query += " AND d.arrival_flight_info LIKE %s"
            filters.append(f"%{arrival_flight_info}%")

        if msg_ref:
            query += " AND d.msg_ref = %s"
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

@diplomats_bp.route('/api/diplomats/monthly-counts', methods=['GET'])
def get_monthly_counts():
    try:
        year = request.args.get('year')
        
        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 2023 or int(year) > datetime.now().year + 1:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get the monthly counts of diplomats grouped by country
        query = """
            SELECT MONTH(arrival_date) AS month, nationality, COUNT(*) AS count
            FROM diplomats
            WHERE YEAR(arrival_date) = %s
            GROUP BY month, nationality
            ORDER BY nationality, month
        """

        cur = mysql.connection.cursor()
        cur.execute(query, (year,))
        results = cur.fetchall()

        country_monthly_data = {}
        grand_total = 0
        for row in results:
            month, nationality, count = row

            # Ensure every country is initialized
            if nationality not in country_monthly_data:
                country_monthly_data[nationality] = {m: 0 for m in range(1, 13)}  # Default to 0 for all months

            # Update the count for the specific month
            country_monthly_data[nationality][month] += count
            grand_total += count

        cur.close()

        # Prepare the final response format
        response_data = {
            "countries": []
        }

        # Add data for each country
        for nationality, months in country_monthly_data.items():
            response_data["countries"].append({
                "nationality": nationality,
                "monthly_counts": [months[month] for month in range(1, 13)],
                "total": sum(months.values())
            })

        # Add the grand total
        response_data["grand_total"] = grand_total

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#retrieves a list of accompaniments for a specific diplomat
@diplomats_bp.route('/api/diplomats/<int:diplomat_id>/accompaniments', methods=['GET'])
def get_accompaniments(diplomat_id):
    try:
        cur = mysql.connection.cursor()

        # Query to fetch accompaniments for the given diplomat_id
        query = "SELECT * FROM diplomat_accompaniment WHERE diplomat_id = %s"
        cur.execute(query, (diplomat_id,))
        results = cur.fetchall()

        # Fetching column names
        column_names = [desc[0] for desc in cur.description]

        # Create a list of dictionaries for each accompaniment
        accompaniments = []
        for row in results:
            accompaniment = dict(zip(column_names, row))
            accompaniments.append(accompaniment)

        cur.close()

        # Return response
        return jsonify({
            "diplomat_id": diplomat_id,
            "accompaniments": accompaniments
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@diplomats_bp.route('/api/diplomats/last-two', methods=['GET'])
def get_last_two_diplomats():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = """
        SELECT 
        d.*, 
        NULL AS dep_msg_ref
        FROM 
        diplomats d
        LEFT JOIN 
        diplomat_departure_logs ddl 
        ON 
        d.id = ddl.diplomat_id
        WHERE 
        ddl.diplomat_id IS NULL
        ORDER BY 
        d.id DESC
        LIMIT 2;
        """
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@diplomats_bp.route('/api/diplomats/<int:diplomat_id>/tourists', methods=['GET'])
def get_tourists_by_diplomat(diplomat_id):
    try:
        cur = mysql.connection.cursor()

        # SQL Query to fetch tourists associated with the given diplomat_id
        query = """
            SELECT 
                t.*, 
                tdl.dep_msg_ref 
            FROM 
                tourists t
            LEFT JOIN 
                diplomat_tourists dt ON t.id = dt.tourist_id
            LEFT JOIN 
                tourist_departure_logs tdl ON t.id = tdl.tourist_id
            WHERE 
                dt.diplomat_id = %s
        """
        
        cur.execute(query, (diplomat_id,))
        results = cur.fetchall()

        # Return results as a list of lists
        cur.close()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500    

@diplomats_bp.route('/api/dipomats/add_departure_log', methods=['POST'])
def add_departure_log():
    data = request.json
    
    # Extract values from the request
    diplomat_id = data.get('diplomat_id')
    departure_method = data.get('departure_method')
    departure_time = data.get('departure_time')
    dep_msg_ref = data.get('dep_msg_ref')

    # Ensure all required fields are provided
    if not diplomat_id or not departure_method or not departure_time:
        return jsonify({"msg": "diplomat_id, departure_method, and departure_time are required!"}), 400
    
    try:
        cursor = mysql.connection.cursor()
        
        # Insert data into tourist_departure_logs table
        insert_query = """
            INSERT INTO diplomat_departure_logs (diplomat_id, departure_method, departure_time, dep_msg_ref)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (diplomat_id, departure_method, departure_time, dep_msg_ref))
        
        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Departure log added successfully!"}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error adding departure log!", "error": str(e)}), 500