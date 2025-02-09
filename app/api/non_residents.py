from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from flask import Blueprint, jsonify

non_residents_bp = Blueprint('non_residents', __name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

#Retrieve All Non-Residents
@non_residents_bp.route('/api/non_residents', methods=['GET'])
def get_all_non_residents():
    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT 
        n.*, 
        ndl.dep_msg_ref  
        FROM 
        non_residents n
        LEFT JOIN 
        non_resident_departure_logs ndl 
        ON 
        n.id = ndl.non_resident_id;
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching non_residents ", "error": str(e)}), 500

@non_residents_bp.route('/api/non_residents/still_in_city', methods=['GET'])
def get_non_residents_still_in_city():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
            n.*,
            ndl.dep_msg_ref  
        FROM 
            non_residents n
        LEFT JOIN 
            non_resident_departure_logs ndl
        ON 
            n.id = ndl.non_resident_id
        WHERE 
            ndl.non_resident_id IS NULL
            AND n.expected_departure_date > CURDATE();
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching non_residents still in the city", "error": str(e)}), 500

@non_residents_bp.route('/api/non_residents/supposed_to_leave', methods=['GET'])
def get_non_residents_supposed_to_leave():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
                n.*,
                ndl.dep_msg_ref  
            FROM 
                non_residents n
            LEFT JOIN 
                non_resident_departure_logs ndl 
            ON 
                n.id = ndl.non_resident_id
            WHERE 
                ndl.non_resident_id IS NULL
                AND (n.expected_departure_date <= CURDATE());
        """
        cursor.execute(query)
        tourists = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in tourists]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching tourists still in the city", "error": str(e)}), 500

#Add a New Non-Resident
@non_residents_bp.route('/api/non_residents/Add', methods=['POST'])
def add_non_resident():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute(""" 
            INSERT INTO non_residents (
                first_name, last_name, date_of_birth, place_of_birth, passport_number,
                passport_expiry, nationality, host, purpose_of_visit, arrival_date,
                expected_departure_date, vehicle_information, observations, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], 
            data.get('place_of_birth'), data['passport_number'], data.get('passport_expiry'),
            data.get('nationality'), data.get('host'), data.get('purpose_of_visit'),
            data['arrival_date'], data.get('expected_departure_date'),
            data.get('vehicle_information'), data.get('observations'), data.get('msg_ref')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Non-resident added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add non-resident'}), 500

@non_residents_bp.route('/api/non_residents/history', methods=['GET'])
def get_non_residents_history():
    try:
        cursor = mysql.connection.cursor()
        
        query = """
        SELECT 
        n.*,
        ndl.dep_msg_ref  
        FROM 
        non_residents n
        INNER JOIN 
        non_resident_departure_logs ndl 
        ON 
        n.id = ndl.non_resident_id;
        """
        cursor.execute(query)
        non_residents = cursor.fetchall()
        
        # Format the result as a single list of records
        result = [list(row) for row in non_residents]
        
        cursor.close()
        return jsonify(result), 200  # Directly return the list

    except Exception as e:
        return jsonify({"msg": "Error fetching non_residents ", "error": str(e)}), 500

#Update a Non-Resident by ID
@non_residents_bp.route('/api/non_residents/Update/<int:id>', methods=['PUT'])
def update_non_resident(id):
    data = request.json
    try:
        # Initialize query and list for fields to update
        update_fields = []
        values = []

        # Check each field, and only add it to the query if it exists in the request data
        if 'host' in data:
            update_fields.append("host = %s")
            values.append(data['host'])

        if 'purpose_of_visit' in data:
            update_fields.append("purpose_of_visit = %s")
            values.append(data['purpose_of_visit'])

        if 'expected_departure_date' in data:
            update_fields.append("expected_departure_date = %s")
            values.append(data['expected_departure_date'])

        if 'vehicle_information' in data:
            update_fields.append("vehicle_information = %s")
            values.append(data['vehicle_information'])

        if 'observations' in data:
            # Fetch the current value of observations
            cur = mysql.connection.cursor()
            cur.execute("SELECT observations FROM non_residents WHERE id = %s", (id,))
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
        query = f"UPDATE non_residents SET {', '.join(update_fields)} WHERE id = %s"
        values.append(id)  # Add the ID to the values list for the WHERE clause

        # Execute the query with the dynamic list of values
        cur = mysql.connection.cursor()
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Non-resident updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

#Delete a Non-Resident by ID    
@non_residents_bp.route('/api/non_residents/Delete/<int:id>', methods=['DELETE'])
def delete_non_resident(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM non_residents WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Non-resident deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#Filter Non-Residents
@non_residents_bp.route('/api/non_residents/filter', methods=['POST'])
def filter_non_residents():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Extract filter parameters
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        nationality = data.get('nationality')
        arrival_date_start = data.get('arrival_date_start')
        arrival_date_end = data.get('arrival_date_end')
        host = data.get('host')
        purpose_of_visit = data.get('purpose_of_visit')
        msg_ref = data.get('msg_ref')

        # Initialize SQL query
        query = """
            SELECT 
                n.*, 
                ndl.dep_msg_ref
            FROM 
                non_residents n
            LEFT JOIN 
                non_resident_departure_logs ndl
            ON 
                n.id = ndl.non_resident_id
            WHERE 1=1
        """
        filters = []

        # Add filters to the query
        if first_name:
            query += " AND n.first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND n.last_name = %s"
            filters.append(last_name)

        if nationality:
            query += " AND n.nationality = %s"
            filters.append(nationality)

        if arrival_date_start and arrival_date_end:
            try:
                arrival_date_start = datetime.strptime(arrival_date_start, '%Y-%m-%d').date()
                arrival_date_end = datetime.strptime(arrival_date_end, '%Y-%m-%d').date()
                query += " AND n.arrival_date BETWEEN %s AND %s"
                filters.extend([arrival_date_start, arrival_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if host:
            query += " AND n.host = %s"
            filters.append(host)

        if purpose_of_visit:
            query += " AND n.purpose_of_visit LIKE %s"
            filters.append(f"%{purpose_of_visit}%")

        if msg_ref:
            query += " AND n.msg_ref = %s"
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

@non_residents_bp.route('/api/non_residents/counts', methods=['GET'])
def get_tourist_counts():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT nationality, COUNT(*) AS count
            FROM non_residents
            GROUP BY nationality
            ORDER BY count DESC;
        """)
        results = cur.fetchall()
        tourist_counts = [{'nationality': row[0], 'count': row[1]} for row in results]

        cur.close()
        return jsonify(tourist_counts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Get Monthly Counts of Non-Residents
@non_residents_bp.route('/api/non_residents/monthly-counts', methods=['GET'])
def get_non_residents_monthly_counts():
    try:
        year = request.args.get('year')
        
        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 2023 or int(year) > datetime.now().year + 1:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get counts grouped by month and nationality
        query = """
            SELECT MONTH(arrival_date) AS month, nationality, COUNT(*) AS count
            FROM non_residents
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

@non_residents_bp.route('/api/non_residents/last-two', methods=['GET'])
def get_last_two_non_residents():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = """
        SELECT 
    n.*,
    ndl.dep_msg_ref,
    ndl.departure_time   
    FROM 
    non_residents n
    LEFT JOIN 
    non_resident_departure_logs ndl 
    ON 
    n.id = ndl.non_resident_id
    ORDER BY 
    n.id DESC
    LIMIT 2;
        """
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@non_residents_bp.route('/api/non_residents/add_departure_log', methods=['POST'])
def add_departure_log():
    data = request.json
    
    # Extract values from the request
    non_resident_id = data.get('non_resident_id')
    departure_method = data.get('observations')
    departure_time = data.get('departure_time')
    dep_msg_ref = data.get('dep_msg_ref')

    # Ensure all required fields are provided
    if not non_resident_id :
        return jsonify({"msg": "non_resident_id  is required!"}), 400
    
    if not departure_method:
         return jsonify({"msg": " departure_method is required!"}), 400

    if not departure_time:
         return jsonify({"msg": "departure_time is required!"}), 400
    
    try:
        cursor = mysql.connection.cursor()
        
        # Insert data into non_resident_departure_logs table
        insert_query = """
            INSERT INTO non_resident_departure_logs (non_resident_id, departure_method, departure_time, dep_msg_ref)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (non_resident_id, departure_method, departure_time, dep_msg_ref))
        
        # Commit the transaction
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Departure log added successfully!"}), 201

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"msg": "Error adding departure log!", "error": str(e)}), 500