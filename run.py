import logging
from app import create_app
from waitress import serve

app = create_app()

# Enable logging for Waitress
logging.basicConfig(level=logging.INFO)  # Adjust level as needed: DEBUG, INFO, WARNING, etc.

if __name__ == "__main__":
    # Use Waitress to serve the application
    serve(app, host='127.0.0.1', port=5001)