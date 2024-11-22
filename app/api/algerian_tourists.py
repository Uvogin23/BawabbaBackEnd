from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from collections import Counter
from flask import Blueprint, jsonify


algerian_tourists_bp = Blueprint('algerian_tourists', __name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

# Retrieve all Algerian tourists
@algerian_tourists_bp.route('/api/algerian_tourists', methods=['GET'])
def get_all_algerian_tourists():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM algerian_tourists")
        results = cur.fetchall()
        cur.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Retrieve a single Algerian tourist by ID
@algerian_tourists_bp.route('/api/algerian_tourists/<int:id>', methods=['GET'])
def get_algerian_tourist(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM algerian_tourists WHERE id = %s", (id,))
        tourist = cur.fetchone()
        cur.close()

        if tourist:
            tourist_data = {
                'id': tourist[0],
                'first_name': tourist[1],
                'last_name': tourist[2],
                'date_of_birth': tourist[3],
                'place_of_birth': tourist[4],
                'id_number': tourist[5],
                'receiving_agency': tourist[6],
                'circuit': tourist[7],
                'arrival_date': tourist[8],
                'touristic_guide': tourist[9],
                'msg_ref': tourist[10],
                'created_at': tourist[11]
            }
            return jsonify(tourist_data), 200
        else:
            return jsonify({'message': 'Tourist not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a new Algerian tourist
@algerian_tourists_bp.route('/api/algerian_tourists/add', methods=['POST'])
def add_algerian_tourist():
    data = request.json
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO algerian_tourists (
                first_name, last_name, date_of_birth, place_of_birth, id_number,
                receiving_agency, circuit, arrival_date, touristic_guide, msg_ref
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['first_name'], data['last_name'], data['date_of_birth'], data.get('place_of_birth'),
            data['id_number'], data.get('receiving_agency'), data.get('circuit'), data.get('arrival_date'),
            data.get('touristic_guide'), data.get('msg_ref')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Tourist added successfully!'}), 201

    except Exception as e:
        return jsonify({'error': 'Failed to add tourist'}), 500

# Update an Algerian tourist by ID
@algerian_tourists_bp.route('/api/algerian_tourists/Update/<int:id>', methods=['PUT'])
def update_algerian_tourist(id):
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
        query = f"UPDATE algerian_tourists SET {', '.join(update_fields)} WHERE id = %s"
        values.algerian_tourists_bpend(id)  # Add the ID to the values list for the WHERE clause

        # Execute the query with the dynamic list of values
        cur = mysql.connection.cursor()
        cur.execute(query, tuple(values))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Tourist updated successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete an Algerian tourist by ID
@algerian_tourists_bp.route('/api/algerian_tourists/Delete/<int:id>', methods=['DELETE'])
def delete_algerian_tourist(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM algerian_tourists WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Tourist deleted successfully!'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get monthly counts of Algerian tourists
@algerian_tourists_bp.route('/api/algerian_tourists/monthly-counts', methods=['GET'])
def get_algerian_tourists_monthly_counts():
    try:
        year = request.args.get('year')

        # Validate the year parameter
        if not year or not year.isdigit() or int(year) < 1900 or int(year) > datetime.now().year:
            return jsonify({"error": "Invalid year parameter. Please provide a valid year."}), 400
        
        year = int(year)

        # Prepare the SQL query to get the monthly counts of Algerian tourists
        query = """
            SELECT MONTH(arrival_date) AS month, COUNT(*) AS count
            FROM algerian_tourists
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
    
@algerian_tourists_bp.route('/api/algerian_tourists/filter', methods=['GET'])
def filter_algerian_tourists():
    try:
        cur = mysql.connection.cursor()
        
        # Get filter parameters from the request
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        receiving_agency = request.args.get('receiving_agency')
        touristic_guide = request.args.get('touristic_guide')
        msg_ref = request.args.get('msg_ref')
        arrival_date_start = request.args.get('arrival_date_start')
        arrival_date_end = request.args.get('arrival_date_end')

        # Start building the SQL query
        query = "SELECT * FROM algerian_tourists WHERE 1=1"
        filters = []

        # Add filters based on provided parameters
        if first_name:
            query += " AND first_name = %s"
            filters.append(first_name)

        if last_name:
            query += " AND last_name = %s"
            filters.append(last_name)
            
        if receiving_agency:
            query += " AND receiving_agency = %s"
            filters.append(receiving_agency)

        if touristic_guide:
            query += " AND touristic_guide = %s"
            filters.append(touristic_guide)

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
            return jsonify({"message": "No Algerian tourists found matching the criteria"}), 404

        # Fetching column names for easier parsing
        column_names = [desc[0] for desc in cur.description]

        # Create a list of dictionaries for each tourist
        tourists = [dict(zip(column_names, row)) for row in results]

        # Count total number of Algerian tourists
        total_count = len(tourists)

        # Count number of tourists by each touristic guide
        guide_counts = Counter(tourist['touristic_guide'] for tourist in tourists)

        cur.close()

        # Create the response data structure
        response_data = {
            "total_algerian_tourists": total_count,
            "guide_counts": dict(guide_counts),
            "algerian_tourists": tourists
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@algerian_tourists_bp.route('/api/algerian_tourists/last-two', methods=['GET'])
def get_last_two_diplomats():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = "SELECT * FROM algerian_tourists ORDER BY id DESC LIMIT 2"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500