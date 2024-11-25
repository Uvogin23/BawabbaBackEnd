from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from datetime import datetime
from datetime import datetime, timedelta
from collections import Counter
from flask import Blueprint, jsonify

stats_bp = Blueprint('stats', __name__)
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wassim-42'
app.config['MYSQL_DB'] = 'BAWABBA'

mysql = MySQL(app)

@stats_bp.route('/api/stats/<string:table_name>', methods=['GET'])
def get_statistics(table_name):
    return get_table_statistics(table_name)

@stats_bp.route('/api/stats/citizens/stats', methods=['GET'])
def citizens_stats():
    return get_citizens_statistics()

@stats_bp.route('/api/stats/overall_counts', methods=['GET'])
def overall_counts():
    return get_overall_counts()


def get_table_statistics(table_name):
    try:
        # Get the current year and the previous year
        current_year = datetime.now().year
        last_year = current_year - 1

        # Create a MySQL cursor
        cursor = mysql.connection.cursor()

        # Query to count total entries in the table
        total_query = f"SELECT COUNT(*) FROM {table_name}"
        cursor.execute(total_query)
        total_count = cursor.fetchone()[0]

        # Query to count entries for the current year
        current_year_query = f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE YEAR(arrival_date) = %s
        """
        cursor.execute(current_year_query, (current_year,))
        current_year_count = cursor.fetchone()[0]

        # Query to count entries for the last year
        last_year_query = f"""
            SELECT COUNT(*) 
            FROM {table_name} 
            WHERE YEAR(arrival_date) = %s
        """
        cursor.execute(last_year_query, (last_year,))
        last_year_count = cursor.fetchone()[0]

        # Close the cursor
        cursor.close()

        # Return results as JSON
        return jsonify({
            "total": total_count,
            "current_year": current_year_count,
            "last_year": last_year_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def get_citizens_statistics():

    try:
        # Get the current year and the previous year
        current_year = datetime.now().year
        last_year = current_year - 1

        # Create a MySQL cursor
        cursor = mysql.connection.cursor()

        # Query to count total entries in the table
        total_query = f"SELECT COUNT(*) FROM citizens"
        cursor.execute(total_query)
        total_count = cursor.fetchone()[0]

        # Query to count entries for the current year
        current_year_query = f"""
            SELECT COUNT(*) 
            FROM citizens
            WHERE YEAR(exit_date) = %s
        """
        cursor.execute(current_year_query, (current_year,))
        current_year_count = cursor.fetchone()[0]

        # Query to count entries for the last year
        last_year_query = f"""
            SELECT COUNT(*) 
            FROM citizens 
            WHERE YEAR(exit_date) = %s
        """
        cursor.execute(last_year_query, (last_year,))
        last_year_count = cursor.fetchone()[0]

        # Close the cursor
        cursor.close()

        # Return results as JSON
        return jsonify({
            "total": total_count,
            "current_year": current_year_count,
            "last_year": last_year_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_overall_counts():
    try:
        # Define table names and their corresponding Arabic labels
        tables = {
            "diplomats": "الدبلوماسيون",
            "algerian_tourists": "السياح الجزائريون",
            "tourists": "السياح الأجانب",
            "diplomat_accompaniment": "المرافقون"
        }

        # Create a MySQL cursor
        cursor = mysql.connection.cursor()

        # Prepare the result dictionary
        result = {}

        # Loop through the tables and get the counts
        for table, label in tables.items():
            query = f"SELECT COUNT(*) FROM {table}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            result[label] = count

        # Close the cursor
        cursor.close()

        # Return results as JSON
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@stats_bp.route('/api/stats/12months', methods=['GET'])
def get_last_twelve_months():
    # Start from the previous month
    current_date = datetime.now()
    last_twelve_months = []

    for i in range(1, 13):  # Start from 1 to exclude the current month
        # Calculate each month's first day starting from the previous month and going backward
        month = (current_date.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        formatted_month = month.strftime('%Y-%m')
        if formatted_month not in last_twelve_months:  # Avoid duplicates
            last_twelve_months.append(formatted_month)

    # Ensure the correct 12 months are included and sort in ascending order
    last_twelve_months = sorted(set(last_twelve_months))[:12]

    # Return the months as a JSON array
    return jsonify(last_twelve_months)

@stats_bp.route('/api/stats/last-12-months-algerian', methods=['GET'])
def get_counts_last_12_months_algerian():
    cursor = mysql.connection.cursor()

    # SQL query to include all months even with count 0
    query = """
    SELECT 
        month_list.month,
        IFNULL(COUNT(t.arrival_date), 0) AS total_count
    FROM 
        (
            SELECT '2023-11' AS month
            UNION ALL SELECT '2023-12'
            UNION ALL SELECT '2024-01'
            UNION ALL SELECT '2024-02'
            UNION ALL SELECT '2024-03'
            UNION ALL SELECT '2024-04'
            UNION ALL SELECT '2024-05'
            UNION ALL SELECT '2024-06'
            UNION ALL SELECT '2024-07'
            UNION ALL SELECT '2024-08'
            UNION ALL SELECT '2024-09'
            UNION ALL SELECT '2024-10'
        ) AS month_list
    LEFT JOIN algerian_tourists t
        ON DATE_FORMAT(t.arrival_date, '%Y-%m') = month_list.month
    GROUP BY month_list.month
    ORDER BY month_list.month ASC;
    """

    # Execute the query
    cursor.execute(query)
    query_results = cursor.fetchall()

    # Extract counts from the query results
    counts = [row[1] for row in query_results]

    # Return the result as JSON
    return jsonify(counts)

@stats_bp.route('/api/stats/last-12-months-tourists', methods=['GET'])
def get_counts_last_12_months_tourists():
    cursor = mysql.connection.cursor()

    # SQL query to include all months even with count 0
    query = """
    SELECT 
        month_list.month,
        IFNULL(COUNT(t.arrival_date), 0) AS total_count
    FROM 
        (
            SELECT '2023-11' AS month
            UNION ALL SELECT '2023-12'
            UNION ALL SELECT '2024-01'
            UNION ALL SELECT '2024-02'
            UNION ALL SELECT '2024-03'
            UNION ALL SELECT '2024-04'
            UNION ALL SELECT '2024-05'
            UNION ALL SELECT '2024-06'
            UNION ALL SELECT '2024-07'
            UNION ALL SELECT '2024-08'
            UNION ALL SELECT '2024-09'
            UNION ALL SELECT '2024-10'
        ) AS month_list
    LEFT JOIN tourists t
        ON DATE_FORMAT(t.arrival_date, '%Y-%m') = month_list.month
    GROUP BY month_list.month
    ORDER BY month_list.month ASC;
    """

    # Execute the query
    cursor.execute(query)
    query_results = cursor.fetchall()

    # Extract counts from the query results
    counts = [row[1] for row in query_results]

    # Return the result as JSON
    return jsonify(counts)

@stats_bp.route('/api/stats/last-12-months-diplomats', methods=['GET'])
def get_counts_last_12_months_diplomats():
    cursor = mysql.connection.cursor()

    # SQL query to include all months even with count 0
    query = """
    SELECT 
        month_list.month,
        IFNULL(COUNT(t.arrival_date), 0) AS total_count
    FROM 
        (
            SELECT '2023-11' AS month
            UNION ALL SELECT '2023-12'
            UNION ALL SELECT '2024-01'
            UNION ALL SELECT '2024-02'
            UNION ALL SELECT '2024-03'
            UNION ALL SELECT '2024-04'
            UNION ALL SELECT '2024-05'
            UNION ALL SELECT '2024-06'
            UNION ALL SELECT '2024-07'
            UNION ALL SELECT '2024-08'
            UNION ALL SELECT '2024-09'
            UNION ALL SELECT '2024-10'
        ) AS month_list
    LEFT JOIN diplomats t
        ON DATE_FORMAT(t.arrival_date, '%Y-%m') = month_list.month
    GROUP BY month_list.month
    ORDER BY month_list.month ASC;
    """

    # Execute the query
    cursor.execute(query)
    query_results = cursor.fetchall()

    # Extract counts from the query results
    counts = [row[1] for row in query_results]

    # Return the result as JSON
    return jsonify(counts)

@stats_bp.route('/api/stats/last-12-months-residents', methods=['GET'])
def get_counts_last_12_months_residents():
    cursor = mysql.connection.cursor()

    # SQL query to include all months even with count 0
    query = """
    SELECT 
        month_list.month,
        IFNULL(COUNT(t.arrival_date), 0) AS total_count
    FROM 
        (
            SELECT '2023-11' AS month
            UNION ALL SELECT '2023-12'
            UNION ALL SELECT '2024-01'
            UNION ALL SELECT '2024-02'
            UNION ALL SELECT '2024-03'
            UNION ALL SELECT '2024-04'
            UNION ALL SELECT '2024-05'
            UNION ALL SELECT '2024-06'
            UNION ALL SELECT '2024-07'
            UNION ALL SELECT '2024-08'
            UNION ALL SELECT '2024-09'
            UNION ALL SELECT '2024-10'
        ) AS month_list
    LEFT JOIN non_residents t
        ON DATE_FORMAT(t.arrival_date, '%Y-%m') = month_list.month
    GROUP BY month_list.month
    ORDER BY month_list.month ASC;
    """

    # Execute the query
    cursor.execute(query)
    query_results = cursor.fetchall()

    # Extract counts from the query results
    counts = [row[1] for row in query_results]

    # Return the result as JSON
    return jsonify(counts)

@stats_bp.route('/api/stats/last-12-months-citizens', methods=['GET'])
def get_counts_last_12_months_citizens():
    cursor = mysql.connection.cursor()

    # SQL query to include all months even with count 0
    query = """
    SELECT 
        month_list.month,
        IFNULL(COUNT(t.exit_date), 0) AS total_count
    FROM 
        (
            SELECT '2023-11' AS month
            UNION ALL SELECT '2023-12'
            UNION ALL SELECT '2024-01'
            UNION ALL SELECT '2024-02'
            UNION ALL SELECT '2024-03'
            UNION ALL SELECT '2024-04'
            UNION ALL SELECT '2024-05'
            UNION ALL SELECT '2024-06'
            UNION ALL SELECT '2024-07'
            UNION ALL SELECT '2024-08'
            UNION ALL SELECT '2024-09'
            UNION ALL SELECT '2024-10'
        ) AS month_list
    LEFT JOIN citizens t
        ON DATE_FORMAT(t.exit_date, '%Y-%m') = month_list.month
    GROUP BY month_list.month
    ORDER BY month_list.month ASC;
    """

    # Execute the query
    cursor.execute(query)
    query_results = cursor.fetchall()

    # Extract counts from the query results
    counts = [row[1] for row in query_results]

    # Return the result as JSON
    return jsonify(counts)



@stats_bp.route('/api/stats/bardata', methods=['GET'])
def get_counts_current_year():
    cursor = mysql.connection.cursor()

    # Get the current year
    current_year = datetime.now().year

    # Queries for each table
    queries = {
         "الدبلوماسيون": f"SELECT COUNT(*) FROM diplomats WHERE YEAR(arrival_date) = {current_year}",
        "السياح الأجانب": f"SELECT COUNT(*) FROM tourists WHERE YEAR(arrival_date) = {current_year}",
        "السياح الجزائريون": f"SELECT COUNT(*) FROM algerian_tourists WHERE YEAR(arrival_date) = {current_year}",
        "المرافقون": f"SELECT COUNT(*) FROM diplomat_accompaniment WHERE YEAR(arrival_date) = {current_year}",
        "الدخول": f"SELECT COUNT(*) FROM non_residents WHERE YEAR(arrival_date) = {current_year}",
        "الخروج": f"SELECT COUNT(*) FROM citizens WHERE YEAR(exit_date) = {current_year}"
    }

    # Execute queries and collect results
    results = {}
    for table, query in queries.items():
        cursor.execute(query)
        count = cursor.fetchone()[0]
        results[table] = count

    return jsonify(results)

@stats_bp.route('/api/stats/last-two/entre', methods=['GET'])
def get_last_two_entre():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = "SELECT * FROM non_residents ORDER BY id DESC LIMIT 2"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route('/api/stats/last-two/sortie', methods=['GET'])
def get_last_two_sortie():
    try:
        cur = mysql.connection.cursor()
        
        # Query to fetch the last two entries
        query = "SELECT * FROM citizens ORDER BY id DESC LIMIT 2"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return jsonify(results)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500