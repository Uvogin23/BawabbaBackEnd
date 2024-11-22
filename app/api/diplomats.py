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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM diplomats")
    results = cur.fetchall()
    cur.close()
    return jsonify(results)

# Retrieve a single diplomat by ID
@diplomats_bp.route('/api/diplomats/<int:id>', methods=['GET'])
def get_diplomat(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM diplomats WHERE id = %s", (id,))
        diplomat = cur.fetchone()
        cur.close()

        if diplomat:
            diplomat_data = {
                'id': diplomat[0],
                'first_name': diplomat[1],
                'last_name': diplomat[2],
                'date_of_birth': diplomat[3],
                'place_of_birth': diplomat[4],
                'passport_number': diplomat[5],
                'passport_expiry': diplomat[6],
                'diplomatic_card_number': diplomat[7],
                'fonction': diplomat[8],
                'nationality': diplomat[9],
                'receiving_agency': diplomat[10],
                'circuit': diplomat[11],
                'arrival_date': diplomat[12],
                'expected_departure_date': diplomat[13],
                'arrival_flight_info': diplomat[14],
                'departure_flight_info': diplomat[15],
                'touristic_guide': diplomat[16],
                'created_at': diplomat[17],
                'msg_ref': diplomat[18]
            }
            return jsonify(diplomat_data), 200
        else:
            return jsonify({'message': 'Diplomat not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a single diplomat
@diplomats_bp.route('/api/diplomats', methods=['POST'])
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
        
        if 'arrival_date' in data:
            update_fields.append("arrival_date = %s")
            values.append(data['arrival_date'])
        
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
@diplomats_bp.route('/api/diplomats/filter', methods=['GET'])
def filter_diplomats():
    try:
        cur = mysql.connection.cursor()
        
        # Get filter parameters from the request
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        nationality = request.args.get('nationality')
        arrival_date_start = request.args.get('arrival_date_start')
        arrival_date_end = request.args.get('arrival_date_end')
        expected_departure_date_start = request.args.get('expected_departure_date_start')
        expected_departure_date_end = request.args.get('expected_departure_date_end')
        receiving_agency = request.args.get('receiving_agency')
        arrival_flight_info = request.args.get('arrival_flight_info')
        touristic_guide = request.args.get('touristic_guide')

        # Start building the SQL query
        query = "SELECT * FROM diplomats WHERE 1=1"
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

        if arrival_date_start and arrival_date_end:
            # Convert to date format for SQL query
            try:
                arrival_date_start = datetime.strptime(arrival_date_start, '%Y-%m-%d').date()
                arrival_date_end = datetime.strptime(arrival_date_end, '%Y-%m-%d').date()
                query += " AND arrival_date BETWEEN %s AND %s"
                filters.extend([arrival_date_start, arrival_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if expected_departure_date_start and expected_departure_date_end:
            # Convert to date format for SQL query
            try:
                expected_departure_date_start = datetime.strptime(expected_departure_date_start, '%Y-%m-%d').date()
                expected_departure_date_end = datetime.strptime(expected_departure_date_end, '%Y-%m-%d').date()
                query += " AND expected_departure_date BETWEEN %s AND %s"
                filters.extend([expected_departure_date_start, expected_departure_date_end])
            except ValueError:
                return jsonify({"error": "Invalid date format for expected_departure_date. Use YYYY-MM-DD."}), 400

        if receiving_agency:
            query += " AND receiving_agency = %s"
            filters.append(receiving_agency)

        if arrival_flight_info:
            query += " AND arrival_flight_info LIKE %s"
            filters.append(f"%{arrival_flight_info}%")  # Use LIKE for partial match

        if touristic_guide:
            query += " AND touristic_guide = %s"
            filters.append(touristic_guide)

        # Log the constructed query and filter values for debugging
        print("Constructed SQL Query:", query)
        print("Filters:", filters)

        # Execute the final query with filters
        cur.execute(query, tuple(filters))
        results = cur.fetchall()

        # Fetching column names
        column_names = [desc[0] for desc in cur.description]

        # Create a list of dictionaries for each diplomat
        diplomats = []
        for row in results:
            diplomat = dict(zip(column_names, row))
            diplomats.append(diplomat)

        # Count total number of diplomats
        total_count = len(diplomats)

        # Count number of diplomats from each country
        nationality_counts = Counter(diplomat['nationality'] for diplomat in diplomats)

        cur.close()

        # Create the response data structure
        response_data = {
            "total_diplomats": total_count,
            "nationality_counts": dict(nationality_counts),
            "diplomats": diplomats
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diplomats_bp.route('/api/diplomats/monthly-counts', methods=['GET'])
def get_monthly_counts():
    try:
        year = request.args.get('year')
        
        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 1900 or int(year) > datetime.now().year:
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

        # Fetching column names
        column_names = [desc[0] for desc in cur.description]

        # Create a structured response
        monthly_counts = {}
        grand_total = 0
        
        for row in results:
            month = row[0]
            nationality = row[1]
            count = row[2]

            if nationality not in monthly_counts:
                monthly_counts[nationality] = {
                    'monthly_counts': [0] * 12,  # Initialize a list for 12 months
                    'total': 0  # Initialize total count for the nationality
                }

            # Update monthly counts and total
            monthly_counts[nationality]['monthly_counts'][month - 1] += count  # Month is 1-indexed
            monthly_counts[nationality]['total'] += count
            grand_total += count

        cur.close()

        # Prepare the final response format
        response_data = {
            "monthly_counts": monthly_counts,
            "grand_total": grand_total
        }

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
        query = "SELECT * FROM diplomats ORDER BY id DESC LIMIT 2"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

