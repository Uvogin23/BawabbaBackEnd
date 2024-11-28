from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from .api import register_blueprints
from flask_jwt_extended import JWTManager


mysql = MySQL()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # MySQL Configuration
    app.config['JWT_SECRET_KEY'] = 'e6a8b42d4e3e5d96f9c4b0d8a7f12c4e9d87c0a62b8a9d1d6e7c8f9b8a1c2d3e'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'wassim-42'
    app.config['MYSQL_DB'] = 'BAWABBA'
    
    mysql.init_app(app)

    # Register all blueprints
    register_blueprints(app)
    jwt = JWTManager(app)

    return app