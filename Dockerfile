# Use Python 3.12 base image
FROM python:3.12-slim

# Install system dependencies, including MySQL
RUN apt-get update && apt-get install -y \
    mysql-server \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Copy the .env file to the container
COPY .env /app/.env

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start MySQL service and set basic login info
RUN service mysql start && \
    mysql -e "CREATE DATABASE IF NOT EXISTS myapp;" && \
    mysql -e "CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'root';" && \
    mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%'; FLUSH PRIVILEGES;"

# Run the Python script to complete the DB schema setup
RUN python setup_database.py

# Expose the necessary ports
EXPOSE 3306 8000

# Entry point to run MySQL and the Python app
CMD service mysql start && \
    python main.py
