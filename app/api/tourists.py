from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from flask import Blueprint, jsonify

tourists_bp = Blueprint('tourists', __name__)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

# Retrieve all tourists
@tourists_bp.route('/api/tourists', methods=['GET'])
def get_tourists():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        t.*, 
        tdl.dep_msg_ref  
        FROM 
        tourists t
        LEFT JOIN 
        tourist_departure_logs tdl 
        ON 
        t.id = tdl.tourist_id;
        """
        cursor.execute(query)
        tourists = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in tourists]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists still in the city", "error": str(e)}), 500

# Retrieve a single tourist by ID
@tourists_bp.route('/api/tourists/<int:id>', methods=['GET'])
def get_tourist(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tourists WHERE id = %s", (id,))
        tourist = cur.fetchone()
        cur.close()

        if tourist:
            tourist_data = {
                'id': tourist[0],
                'first_name': tourist[1],
                'last_name': tourist[2],
                'date_of_birth': tourist[3],
                'place_of_birth': tourist[4],
                'passport_number': tourist[5],
                'passport_expiry': tourist[6],
                'nationality': tourist[7],
                'receiving_agency': tourist[8],
                'circuit': tourist[9],
                'arrival_date': tourist[10],
                'expected_departure_date': tourist[11],
                'arrival_flight_info': tourist[12],
                'departure_flight_info': tourist[13],
                'touristic_guide': tourist[14],
                'msg_ref': tourist[15],
                'created_at': tourist[16]
                

            }
            return jsonify(tourist_data), 200
        else:
            return jsonify({'message': 'Tourist not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@tourists_bp.route('/api/tourists/still_in_city', methods=['GET'])
def get_tourists_still_in_city():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
            t.*,
            tdl.dep_msg_ref  
        FROM 
            tourists t
        LEFT JOIN 
            tourist_departure_logs tdl
        ON 
            t.id = tdl.tourist_id
        WHERE 
            tdl.tourist_id IS NULL
            AND t.expected_departure_date > CURDATE();
        """
        cursor.execute(query)
        tourists = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in tourists]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists still in the city", "error": str(e)}), 500
    
@tourists_bp.route('/api/tourists/supposed_to_leave', methods=['GET'])
def get_tourists_supposed_to_leave():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
                t.*,
                tdl.dep_msg_ref  
            FROM 
                tourists t
            LEFT JOIN 
                tourist_departure_logs tdl 
            ON 
                t.id = tdl.tourist_id
            WHERE 
                tdl.tourist_id IS NULL
                AND (t.expected_departure_date <= CURDATE());
        """
        cursor.execute(query)
        tourists = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in tourists]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists still in the city", "error": str(e)}), 500
    
@tourists_bp.route('/api/tourists/history', methods=['GET'])
def get_tourists_history():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        t.*,
        tdl.dep_msg_ref  
        FROM 
        tourists t
        INNER JOIN 
        tourist_departure_logs tdl 
        ON 
        t.id = tdl.tourist_id;
        """
        cursor.execute(query)
        tourists = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in tourists]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists ", "error": str(e)}), 500
    
# Add a single tourist
@tourists_bp.route('/api/tourists/Add', methods=['POST'])
def add_tourist():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tourists (
                first_name, last_name, date_of_birth, place_of_birth, passport_number, passport_expiry,
                nationality, receiving_agency, circuit, arrival_date, expected_departure_date,
                arrival_flight_info, departure_flight_info, touristic_guide, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data['place_of_birth'],
            data['passport_number'], data['passport_expiry'], data['nationality'],
            data['receiving_agency'], data['circuit'], data['arrival_date'], 
            data['expected_departure_date'], data['arrival_flight_info'], 
            data['departure_flight_info'], data['touristic_guide'], data['msg_ref']
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Tourist added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add tourist'}), 500

#Add tourists associated with diplomats
@tourists_bp.route('/api/tourists/AddTD', methods=['POST'])
def add_tourist_dip():
    data = request.json
    try:
        cur = mysql.connection.cursor()

        # Step 1: Add a new tourist
        cur.execute("""
            INSERT INTO tourists (
                first_name, last_name, date_of_birth, place_of_birth, passport_number, passport_expiry,
                nationality, receiving_agency, circuit, arrival_date, expected_departure_date,
                arrival_flight_info, departure_flight_info, touristic_guide, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data['place_of_birth'],
            data['passport_number'], data['passport_expiry'], data['nationality'],
            data['receiving_agency'], data['circuit'], data['arrival_date'], 
            data['expected_departure_date'], data['arrival_flight_info'], 
            data['departure_flight_info'], data['touristic_guide'], data['msg_ref']
        ))
        mysql.connection.commit()

        # Get the ID of the newly added tourist
        tourist_id = cur.lastrowid

        # Step 2: Fetch the last diplomat ID
        cur.execute("SELECT id FROM diplomats ORDER BY id DESC LIMIT 1")
        diplomat = cur.fetchone()

        if diplomat:
            # If the query returns a row, extract the diplomat ID
            diplomat_id = diplomat[0] if isinstance(diplomat, tuple) else diplomat['id']

            # Step 3: Insert into the diplomat_tourists table
            cur.execute("""
                INSERT INTO diplomat_tourists (diplomat_id, tourist_id)
                VALUES (%s, %s)
            """, (diplomat_id, tourist_id))
            mysql.connection.commit()

            cur.close()

            return jsonify({
                'message': 'Tourist added and association created successfully!',
                'last_diplomat_id': diplomat_id,
                'new_tourist_id': tourist_id
            }), 201

        else:
            cur.close()
            return jsonify({'error': 'No diplomats found in the database. Cannot associate tourist.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a tourist by ID
@tourists_bp.route('/api/tourists/Delete/<int:id>', methods=['DELETE'])
def delete_tourist(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tourists WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Tourist deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a tourist by ID
@tourists_bp.route('/api/tourists/Update/<int:id>', methods=['PUT'])
def update_tourist(id):
    data = request.json
    try:
        # Prepare the update query with optional fields
        query_parts = []
        params = []

        if 'receiving_agency' in data:
            query_parts.append("receiving_agency = %s")
            params.append(data['receiving_agency'])
        
        if 'circuit' in data:
            query_parts.append("circuit = %s")
            params.append(data['circuit'])
        
        if 'expected_departure_date' in data:
            query_parts.append("expected_departure_date = %s")
            params.append(data['expected_departure_date'])
        
        if 'arrival_flight_info' in data:
            query_parts.append("arrival_flight_info = %s")
            params.append(data['arrival_flight_info'])
        
        if 'departure_flight_info' in data:
            query_parts.append("departure_flight_info = %s")
            params.append(data['departure_flight_info'])

        if 'touristic_guide' in data:
            query_parts.append("touristic_guide = %s")
            params.append(data['touristic_guide'])

        if 'msg_ref' in data:
            query_parts.append("msg_ref = %s")
            params.append(data.get('msg_ref'))

        # Add the ID to the parameters
        params.append(id)

        if not query_parts:
            return jsonify({'message': 'No fields to update.'}), 400

        # Combine query parts into a single query
        query = f"UPDATE tourists SET {', '.join(query_parts)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Tourist updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tourists sorted by nationality
@tourists_bp.route('/api/tourists/bynationality', methods=['GET'])
def get_tourists_by_nationality():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tourists ORDER BY nationality ASC;")
        results = cur.fetchall()

        column_names = [desc[0] for desc in cur.description]
        tourists = [dict(zip(column_names, row)) for row in results]

        cur.close()
        return jsonify(tourists), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Number of tourists from each country
@tourists_bp.route('/api/tourists/counts', methods=['GET'])
def get_tourist_counts():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT nationality, COUNT(*) AS count
            FROM tourists
            GROUP BY nationality
            ORDER BY count DESC;
        """)
        results = cur.fetchall()
        tourist_counts = [{'nationality': row[0], 'count': row[1]} for row in results]

        cur.close()
        return jsonify(tourist_counts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Show tourists from a specific country
@tourists_bp.route('/api/tourists/country/<string:nationality>', methods=['GET'])
def get_tourists_by_country(nationality):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tourists WHERE nationality = %s;", (nationality,))
        results = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        tourists = [dict(zip(column_names, row)) for row in results]

        cur.close()
        return jsonify(tourists), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Filter tourists
@tourists_bp.route('/api/tourists/filter', methods=['POST'])
def filter_tourists():
    try:
        # Get JSON data from the request
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

        # Initialize SQL query
        query = """
            SELECT 
                t.*, 
                tdl.dep_msg_ref
            FROM 
                tourists t
            LEFT JOIN 
                tourist_departure_logs tdl
            ON 
                t.id = tdl.tourist_id
            WHERE 1=1
        """
        filters = []

        # Add filters to the query
        if first_name:
            query += " AND t.first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND t.last_name = %s"
            filters.append(last_name)

        if nationality:
            query += " AND t.nationality = %s"
            filters.append(nationality)

        if arrival_date_start and arrival_date_end:
            try:
                arrival_date_start = datetime.strptime(arrival_date_start, '%Y-%m-%d').date()
                arrival_date_end = datetime.strptime(arrival_date_end, '%Y-%m-%d').date()
                query += " AND t.arrival_date BETWEEN %s AND %s"
                filters.extend([arrival_date_start, arrival_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if receiving_agency:
            query += " AND t.receiving_agency = %s"
            filters.append(receiving_agency)

        if arrival_flight_info:
            query += " AND t.arrival_flight_info LIKE %s"
            filters.append(f"%{arrival_flight_info}%")

        if msg_ref:
            query += " AND t.msg_ref = %s"
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

@tourists_bp.route('/api/tourists/monthly_counts', methods=['GET'])
def get_tourist_monthly_counts():
    try:
        year = request.args.get('year')
        
        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 2023 or int(year) > datetime.now().year + 1:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get counts grouped by month and nationality
        query = """
            SELECT MONTH(arrival_date) AS month, nationality, COUNT(*) AS count
            FROM tourists
            WHERE YEAR(arrival_date) = %s
            GROUP BY month, nationality
            ORDER BY nationality, month
        """

        cur = mysql.connection.cursor()
        cur.execute(query, (year,))
        results = cur.fetchall()

        # Initialize the response structure
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

@tourists_bp.route('/api/tourists/last-two', methods=['GET'])
def get_last_two_tourists():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = """
        SELECT 
    t.*, 
    NULL AS dep_msg_ref
FROM 
    tourists t
LEFT JOIN 
    tourist_departure_logs tdl 
ON 
    t.id = tdl.tourist_id
WHERE 
    tdl.tourist_id IS NULL
ORDER BY 
    t.id DESC
LIMIT 2;
"""
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tourists_bp.route('/api/tourists/add_departure_log', methods=['POST'])
def add_departure_log():
    data = request.json
    
    # Extract values from the request
    tourist_id = data.get('tourist_id')
    departure_method = data.get('departure_method')
    departure_time = data.get('departure_time')
    dep_msg_ref = data.get('dep_msg_ref')

    # Ensure all required fields are provided
    if not tourist_id or not departure_method or not departure_time:
        return jsonify({"msg": "tourist_id, departure_method, and departure_time are required!"}), 400
    
    try:
        cursor = mysql.connection.cursor()
        
        # Insert data into tourist_departure_logs table
        insert_query = """
            INSERT INTO tourist_departure_logs (tourist_id, departure_method, departure_time, dep_msg_ref)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (tourist_id, departure_method, departure_time, dep_msg_ref))
        
        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Departure log added successfully!"}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error adding departure log!", "error": str(e)}), 500