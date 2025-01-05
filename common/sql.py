import mysql.connector
from common.utils import getSqlCreds
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def createConnection(**kwargs: dict[str, str]):
    try:
        connection = mysql.connector.connect(**getSqlCreds())
        if connection.is_connected():
            logging.debug(f"Inside SQL Module connections established")
            return connection, connection.cursor() 
    except mysql.connector.Error as error:
        logging.error(f"Error connecting to MySQL: {error}")
    return None, None

def closeConnections(connection = None, cursor = None):
    if cursor:
        try:
            cursor.close()
            logging.info("Cursor is closed")
        except mysql.connector.Error as error:
            logging.info(f"Error closing cursor: {error}")
    if connection:
        try:
            connection.close()
            logging.info("MySQL connection is closed")
        except mysql.connector.Error as error:
            logging.error(f"Error closing connection: {error}")

#wrapper for db connections to absratc away conenctions logic
def manageDatabaseConnections(func):
    def connectionsHandler(*args, **kwargs):
        connection, cursor = createConnection()
        if connection and cursor:
            try:
                result = func(connection, cursor, *args, **kwargs)
                connection.commit()
                return result
            except mysql.connector.Error as error:
                logging.error(f"An error occurred: {error}")
                connection.rollback()  
            finally:
                closeConnections(connection, cursor)
        else:
            logging.error("Failed to establish database connection")
    return connectionsHandler