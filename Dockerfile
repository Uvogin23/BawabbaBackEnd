# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the 'bawabba' folder into the container's /app directory
COPY . .

# Expose the port the app runs on (Flask default is 5000)
EXPOSE 5000

# Set environment variable to specify the entry point of the app
ENV FLASK_APP=run.py

# Run the Flask application
CMD ["python", "run.py"]