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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tourists")
    results = cur.fetchall()
    cur.close()
    return jsonify(results), 200

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
@tourists_bp.route('/api/tourists/filter', methods=['GET'])
def filter_tourists():
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
        query = "SELECT * FROM tourists WHERE 1=1"
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
        tourists = [dict(zip(column_names, row)) for row in results]

        cur.close()
        return jsonify(tourists), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#retrieving monthly counts of tourists
@tourists_bp.route('/api/tourists/monthly-counts', methods=['GET'])
def get_tourist_monthly_counts():
    try:
        year = request.args.get('year')
        
        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 1900 or int(year) > datetime.now().year:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get the monthly counts of tourists grouped by country
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


@tourists_bp.route('/api/tourists/last-two', methods=['GET'])
def get_last_two_tourists():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = "SELECT * FROM tourists ORDER BY id DESC LIMIT 2"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@tourists_bp.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, alpha_2, alpha_3, name FROM countries")
        countries = cursor.fetchall()
        
        # Convert query results into a list of dictionaries
        country_list = []
        for country in countries:
            country_list.append({
                'id': country[0],
                'alpha_2': country[1],
                'alpha_3': country[2],
                'name': country[3]
            })

        cursor.close()
        return jsonify(country_list), 200

    except Exception as e:
        return jsonify({"msg": "Error fetching countries", "error": str(e)}), 500