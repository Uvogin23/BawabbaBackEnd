import logging
from app import create_app
from waitress import serve

app = create_app()

# Enable logging for Waitress
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)