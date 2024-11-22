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
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM non_residents")
        results = cur.fetchall()
        cur.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Retrieve a Single Non-Resident by ID   
@non_residents_bp.route('/api/non_residents/<int:id>', methods=['GET'])
def get_non_resident(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM non_residents WHERE id = %s", (id,))
        non_resident = cur.fetchone()
        cur.close()

        if non_resident:
            non_resident_data = {
                'id': non_resident[0],
                'first_name': non_resident[1],
                'last_name': non_resident[2],
                'date_of_birth': non_resident[3],
                'place_of_birth': non_resident[4],
                'passport_number': non_resident[5],
                'passport_expiry': non_resident[6],
                'nationality': non_resident[7],
                'host': non_resident[8],
                'purpose_of_visit': non_resident[9],
                'arrival_date': non_resident[10],
                'expected_departure_date': non_resident[11],
                'vehicle_information': non_resident[12],
                'message_reference': non_resident[13],
                'observations': non_resident[14],
                'created_at': non_resident[15],
                'msg_ref': non_resident[16],
            }
            return jsonify(non_resident_data), 200
        else:
            return jsonify({'message': 'Non-resident not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
                expected_departure_date, vehicle_information, message_reference,
                observations, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], 
            data.get('place_of_birth'), data['passport_number'], data.get('passport_expiry'),
            data.get('nationality'), data.get('host'), data.get('purpose_of_visit'),
            data['arrival_date'], data.get('expected_departure_date'),
            data.get('vehicle_information'), data.get('message_reference'),
            data.get('observations'), data.get('msg_ref')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Non-resident added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add non-resident'}), 500


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

        if 'message_reference' in data:
            update_fields.append("message_reference = %s")
            values.append(data['message_reference'])

        if 'observations' in data:
            update_fields.append("observations = %s")
            values.append(data['observations'])

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
@non_residents_bp.route('/api/non_residents/filter', methods=['GET'])
def filter_non_residents():
    try:
        cur = mysql.connection.cursor()
        
        # Get filter parameters from the request
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        nationality = request.args.get('nationality')
        msg_ref = request.args.get('msg_ref')
        arrival_date_start = request.args.get('arrival_date_start')
        arrival_date_end = request.args.get('arrival_date_end')

        # Start building the SQL query
        query = "SELECT * FROM non_residents WHERE 1=1"
        filters = []

        # Add filters based on provided parameters
        if first_name:
            query += " AND first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND last_name = %s"
            filters.append(last_name)
            
        if nationality:
            query += " AND nationality = %s"
            filters.append(nationality)

        if msg_ref:
            query += " AND msg_ref = %s"
            filters.append(msg_ref)

        if arrival_date_start and arrival_date_end:
            # Convert to date format for SQL query
            try:
                arrival_date_start = datetime.strptime(arrival_date_start, '%Y-%m-%d').date()
                arrival_date_end = datetime.strptime(arrival_date_end, '%Y-%m-%d').date()
                query += " AND arrival_date BETWEEN %s AND %s"
                filters.extend([arrival_date_start, arrival_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Log the constructed query and filter values for debugging
        print("Constructed SQL Query:", query)
        print("Filters:", filters)

        # Execute the final query with filters
        cur.execute(query, tuple(filters))
        results = cur.fetchall()

        # Check if results are empty and return appropriate message
        if not results:
            return jsonify({"message": "No non-residents found matching the criteria"}), 404

        # Fetching column names for easier parsing
        column_names = [desc[0] for desc in cur.description]

        # Create a list of dictionaries for each non-resident
        non_residents = [dict(zip(column_names, row)) for row in results]

        # Count total number of non-residents
        total_count = len(non_residents)

        # Count number of non-residents from each country
        nationality_counts = Counter(non_resident['nationality'] for non_resident in non_residents)

        cur.close()

        # Create the response data structure
        response_data = {
            "total_non_residents": total_count,
            "nationality_counts": dict(nationality_counts),
            "non_residents": non_residents
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Get Monthly Counts of Non-Residents
@non_residents_bp.route('/api/non_residents/monthly-counts', methods=['GET'])
def get_non_residents_monthly_counts():
    try:
        year = request.args.get('year')

        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 1900 or int(year) > datetime.now().year:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get the monthly counts of non-residents
        query = """
            SELECT MONTH(arrival_date) AS month, COUNT(*) AS count
            FROM non_residents
            WHERE YEAR(arrival_date) = %s
            GROUP BY month
            ORDER BY month
        """

        cur = mysql.connection.cursor()
        cur.execute(query, (year,))
        results = cur.fetchall()
        cur.close()

        # Structure response data
        monthly_counts = {i: 0 for i in range(1, 13)}  # Initialize months with zero counts
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
