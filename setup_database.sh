#!/bin/bash

# Function to print a message and read user input
read_input() {
  local prompt="$1"
  local default_value="$2"
  local input

  read -p "$prompt" input
  echo "${input:-$default_value}"
}

# Function to import MySQL schema
import_mysql_schema() {
  echo "Importing MySQL schema from the file..."

  # Check if the schema file exists
  if [[ ! -f "$SCHEMA_FILE" ]]; then
    echo "Schema file $SCHEMA_FILE not found. Please provide a valid file."
    exit 1
  fi

  # Create the database if it doesn't exist
  mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"

  # Import the schema into the database
  mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DATABASE" < "$SCHEMA_FILE"
  echo "Schema import complete."
}

# Prompt user for environment details
echo "Let's set up your MySQL schema import."
MYSQL_USER=$(read_input "Enter MySQL username [default: root]: " "root")
MYSQL_PASSWORD=$(read_input "Enter MySQL password [default: root]: " "root")
MYSQL_HOST=$(read_input "Enter MySQL host [default: localhost]: " "localhost")
MYSQL_DATABASE=$(read_input "Enter MySQL database name [default: israelrealtimedb]: " "israelrealtimedb")

# Ask for the path to the schema file
SCHEMA_FILE=$(read_input "Enter the path to your MySQL schema file [default: ./israelrealtimedb_schema.sql]: " "./israelrealtimedb_schema.sql")

# Save the credentials to a file
CREDENTIALS_FILE="sql_login_info"
echo "Saving your MySQL credentials to $CREDENTIALS_FILE..."
cat <<EOL > $CREDENTIALS_FILE
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_HOST=$MYSQL_HOST
MYSQL_DATABASE=$MYSQL_DATABASE
EOL

chmod 600 $CREDENTIALS_FILE  # Secure the file

# Import the schema
import_mysql_schema

# Final instructions
cat <<EOF

Setup Complete!

1. The schema has been imported into the $MYSQL_DATABASE database.
2. Use the following credentials to log in to MySQL or a GUI tool like MySQL Workbench:
   - Username: $MYSQL_USER
   - Password: $MYSQL_PASSWORD
   - Host: $MYSQL_HOST
   - Database: $MYSQL_DATABASE
3. Remember to configure the GUI tool with the same username and password.

Credentials saved in: $CREDENTIALS_FILE (keep it secure!).
EOF
