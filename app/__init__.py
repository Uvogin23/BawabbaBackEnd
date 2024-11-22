from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from .api import register_blueprints


mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # MySQL Configuration
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'wassim-42'
    app.config['MYSQL_DB'] = 'BAWABBA'

    mysql.init_app(app)

    # Register all blueprints
    register_blueprints(app)

    return app