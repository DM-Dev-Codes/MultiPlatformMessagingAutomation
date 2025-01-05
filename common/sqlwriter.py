from common.sql import manageDatabaseConnections
import os
import io
import base64
from PIL import Image
import logging
from pathlib import Path
from common.utils import jsonLoader,  deleteFilesInDir

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# base_dir = Path(__file__).resolve().parent.parent 
# IMAGE_DIR = os.getenv("IMAGE_DIR")
# VID_DIR = os.getenv("VID_DIR")
METADATA_FILE = os.getenv("METADATA_FILE")

@manageDatabaseConnections
def writeMetadata(connection, cursor, msg_dict: dict):
    insert_metadata_sql = """INSERT INTO Metadata 
            (message_id, date_year, date_month, date_day, 
            date_hour, date_minute, date_second, 
            user_id, chat_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    val = (
    msg_dict.get("message_id"),
    msg_dict.get("date", {}).get("year"),
    msg_dict.get("date", {}).get("month"),
    msg_dict.get("date", {}).get("day"),
    msg_dict.get("date", {}).get("hour"),
    msg_dict.get("date", {}).get("minute"),
    msg_dict.get("date", {}).get("second"),
    msg_dict.get("user", {}).get("id"),
    msg_dict.get("chat_id"),
    )
    cursor.execute(insert_metadata_sql, val)
    logging.info(f"Record inserted successfully into Metadata table")
 
@manageDatabaseConnections   
def writeMediaDb(connection, cursor, text_id, media_type, media_byte_list):
    if media_byte_list:
        media_config = {
        "picture": {"table": "Picture", "column": "image_blob"},
        "video": {"table": "Video", "column": "video_data"}
        }
        if media_type.lower() not in media_config:
            print(f"Unsupported media type: ")
            return
        insert_config = media_config[media_type]
        insert_cmd = f"INSERT INTO {insert_config['table']} (text_id, {insert_config['column']}) VALUES (%s, %s)"
        for media_base64 in media_byte_list:
            media_blob = base64.b64decode(media_base64)  
            cursor.execute(insert_cmd, (text_id, media_blob))
      
@manageDatabaseConnections                       
def writeMsgDb(connection, cursor):
    msg_dict = jsonLoader(METADATA_FILE)
    media_types_dirs = [("picture", msg_dict["media"]["images"]), ("video", msg_dict["media"]["videos"])]
    logging.info(f" write msg db videos list{msg_dict["media"]["videos"]}")
    logging.debug(f"the sql writing module ")
    if msg_dict:
        logging.debug(f"Parsed message: {connection} {cursor}")
        if  connection and cursor:
            msg_text = msg_dict.get('content', {}).get('text')
            msg_id = msg_dict.get('message_id')
            sql = "INSERT INTO Text (text_content, text_id) VALUES (%s, %s)"
            cursor.execute(sql, (msg_text, msg_id))
            connection.commit()
            print(f"Text inserted successfully with ID: ")
            for media_type, media_byte_list in media_types_dirs:
                writeMediaDb(msg_id, media_type, media_byte_list)
            writeMetadata(msg_dict)
            return True
    else:
        logging.error("Failed to load message metadata.")
        return False

@manageDatabaseConnections   
def readMsgDb(connection, cursor):
    retrieve_data_query =  """SELECT t.text_id, t.text_content, p.image_blob, v.video_data
        FROM text t
        LEFT JOIN picture p ON t.text_id = p.text_id
        LEFT JOIN video v ON t.text_id = v.text_id
        WHERE t.text_id = (SELECT MAX(text_id) FROM text)
        LIMIT 1;
    """
    cursor.execute(retrieve_data_query)
    query_results = cursor.fetchall()
    return query_results
    
    
@manageDatabaseConnections 
def writeGroupNames(connection, cursor, group_names: list):
    insert_query = "INSERT INTO whatsapp_groups (group_name) VALUES (%s)"
    for group_name in group_names:
            cursor.execute(insert_query, (group_name,))
            
@manageDatabaseConnections
def eraseGroupName(connection, cursor, group_name: str):
    delete_query = "DELETE FROM whatsapp_groups WHERE group_name = %s"
    cursor.execute(delete_query, (group_name,))


@manageDatabaseConnections     
def readGroupNamesDB(connection, cursor):
    query = "SELECT group_name FROM whatsapp_groups"
    cursor.execute(query)
    query_results = cursor.fetchall()
    group_names = [group[0] for group in query_results] 
    return group_names

@manageDatabaseConnections     
def writeConstantMessages(connection, cursor, message_type: str, message_content: str):
    insert_query = """
    INSERT INTO constant_message (message_type, message_text)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    message_text = VALUES(message_text);
    """
    cursor.execute(insert_query, (message_type, message_content))


@manageDatabaseConnections
def readConstantMessages(connection, cursor, message_type: str):
    select_query = "SELECT message_text FROM constant_message WHERE message_type = %s"
    cursor.execute(select_query, (message_type,))
    result = cursor.fetchone()
    if result:
        return result[0] 
    else:
        return None  
    
def parseQuery():
    query_dict = {
        'text': None,
        'images_as_bytes': [],
        'videos_as_bytes': [],
    }
    query_result = readMsgDb()  
    if query_result:
        for row in query_result:
            _, text_content, image_blob, video_blob = row
            if text_content and not query_dict['text']:
                query_dict['text'] = text_content
            if image_blob:
                query_dict['images_as_bytes'].append(image_blob)
            if video_blob:
                query_dict['videos_as_bytes'].append(video_blob)
    logging.info(f"this is the quaried dict:{len(query_dict)}")
    return query_dict
