# Function to print a message and read user input
function Read-Input {
    param (
        [string]$Prompt,
        [string]$DefaultValue
    )
    
    $input = Read-Host "$Prompt"
    if ([string]::IsNullOrWhiteSpace($input)) {
        return $DefaultValue
    }
    return $input
}

# Function to import MySQL schema
function Import-MySQLSchema {
    param (
        [string]$SchemaFile
    )
    
    Write-Host "Importing MySQL schema from the file..."

    # Check if the schema file exists
    if (-not (Test-Path $SchemaFile)) {
        Write-Host "Schema file $SchemaFile not found. Please provide a valid file."
        exit 1
    }

    # Create the database if it doesn't exist
    $createDbCommand = "CREATE DATABASE IF NOT EXISTS $MYSQL_DATABASE;"
    mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_HOST -e $createDbCommand

    # Import the schema into the database
    $importCommand = "mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_HOST $MYSQL_DATABASE < $SchemaFile"
    Invoke-Expression $importCommand

    Write-Host "Schema import complete."
}

# Function to configure MySQL
function Configure-MySQL {
    Write-Host "Let's set up your MySQL environment."

    $MYSQL_USER = Read-Input "Enter MySQL username [default: root]: " "root"
    $MYSQL_PASSWORD = Read-Input "Enter MySQL password [default: root]: " "root"
    $MYSQL_HOST = Read-Input "Enter MySQL host [default: localhost]: " "localhost"
    $MYSQL_DATABASE = Read-Input "Enter MySQL database name [default: israelrealtimedb]: " "israelrealtimedb"
    $SCHEMA_FILE = Read-Input "Enter the path to your MySQL schema file [default: ./israelrealtimedb_schema.sql]: " "./israelrealtimedb_schema.sql"

    # Save credentials to a file
    $CREDENTIALS_FILE = "sql_login_info.txt"
    Write-Host "Saving your MySQL credentials to $CREDENTIALS_FILE..."
    $credentials = @"
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_HOST=$MYSQL_HOST
MYSQL_DATABASE=$MYSQL_DATABASE
"@
    $credentials | Out-File -FilePath $CREDENTIALS_FILE -Encoding UTF8
    Set-ItemProperty -Path $CREDENTIALS_FILE -Name "IsReadOnly" -Value $true # Secure the file

    Write-Host "MySQL credentials saved securely."
}

# Function to start MySQL service
function Start-MySQLService {
    Write-Host "Starting MySQL service..."
    Start-Service -Name "MySQL" -ErrorAction SilentlyContinue
    Write-Host "MySQL service started."
}

# Main Execution
Write-Host "Checking if MySQL is installed..."

# Check if MySQL is installed
$mysqlInstalled = Get-Command "mysql" -ErrorAction SilentlyContinue
if (-not $mysqlInstalled) {
    Write-Host "MySQL is not installed. Please install MySQL manually."
    exit 1
} else {
    Write-Host "MySQL is already installed."
}

# Configure MySQL
Configure-MySQL

# Import the schema
Import-MySQLSchema -SchemaFile $SCHEMA_FILE

# Start MySQL service
Start-MySQLService

# Final instructions
Write-Host "
Setup Complete!

1. The schema has been imported into the $MYSQL_DATABASE database.
2. Use the following credentials to log in to MySQL or a GUI tool like MySQL Workbench:
   - Username: $MYSQL_USER
   - Password: $MYSQL_PASSWORD
   - Host: $MYSQL_HOST
   - Database: $MYSQL_DATABASE
3. Remember to configure the GUI tool with the same username and password.

Credentials saved in: $CREDENTIALS_FILE (keep it secure!).
"
