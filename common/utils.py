import json
import os
from pathlib import Path
# from telethon.errors import FloodWaitError, FilePartMissingError, RPCError
import tempfile
from typing import Dict, Any
from collections.abc import KeysView
import asyncio
import base64
from dotenv import load_dotenv
load_dotenv()
import logging


    
#parses and returns meta data
def parseMessageMetadata(event: list, tmp_media_files: list ) -> Dict[str, Any]:
    messages = event if isinstance(event, list) else [event]
    metadata = {
        "message_id": None,
        "date": {
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
            "minute": None,
            "second": None
        },
        "content": {
            "text": None
        },
        "user": {
            "id": None
        },
        "chat_id": "",
        "media": {"images":[], "videos": []},
    }
    for msg in messages:
        if not metadata["content"]["text"] and msg.message:
            metadata["content"]["text"] = msg.message
            if metadata["message_id"] is None:
                metadata["message_id"] = msg.id
                metadata["user"]["id"] = msg.sender_id
                metadata["chat_id"] = msg.chat_id
                metadata["date"] = {
                    "year": msg.date.year,
                    "month": msg.date.month,
                    "day": msg.date.day,
                    "hour": msg.date.hour,
                    "minute": msg.date.minute,
                    "second": msg.date.second
                }
    if tmp_media_files:
        media_mapping = {
            '.jpeg': 'images',
            '.png': 'images',
            '.jpg': 'images',
            '.mp4': 'videos'
        }
        for media_file in tmp_media_files:
            tmp_file_path = Path(media_file)
            if tmp_file_path.suffix in media_mapping:
                media_type = media_mapping[tmp_file_path.suffix]  
                base64_data = base64.b64encode(tmp_file_path.read_bytes()).decode('utf-8')
                metadata["media"][media_type].append(base64_data)
        clearTempFiles(tmp_media_files)
    # logging.debug(f"this is the metadata: {metadata}")
    # logging.info(f"this is the metadata: {metadata["media"]}")
    return metadata


     
# handle creating/writing parsed metadata to file in json format
def jsonLoader(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
    else:
        print(f"File: {file_path} not found")
        return None
    
import logging  
def jsonWriter(data, file_path):
    try:
        logging.info(f"data in untils json write {data}")
        # Open the file in append mode
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            json_file.write('\n')  # Ensure each entry is on a new line
        logging.debug(f"Data successfully written to {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to write data to {file_path}: {e}")
        return False
         
#might not need this as i write to databse and read from there no mroe temp
def ensureDirectoriesExist(dir_names: list):
    for directory in dir_names:
        if not os.path.exists(directory):
            os.makedirs(directory)        
        
def deleteFilesInDir(dir_path):
    dir_path = Path(dir_path)
    if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()  

def getTwitterCreds():
    return{
        "bearer_token" : os.getenv("BEARER_TOKEN"),
        "consumer_key" : os.getenv("CONSUMER_KEY"),
        "consumer_secret" : os.getenv("CONSUMER_SECRET"),
        "access_token" : os.getenv("ACCESS_TOKEN"),
        "access_token_secret" : os.getenv("ACCESS_TOKEN_SECRET")
        }

def getSqlCreds():
    return {
    "host" : os.getenv('HOST'),
    "user" : os.getenv('USER'),
    "password" : os.getenv('PASSWORD'),
    "database" : os.getenv('DATABASE')
    }
    
def getBloggerCreds():
    return json.loads(os.getenv("CLIENT_SECRETS_JSON"))



def bundleMessageForProcess(selected_group: str, msg_text: str, uploaded_files: list):
    msg_dict = {
        'group_name': selected_group,
        'text_content': msg_text,
        'media_files': []
    }
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix, dir="/tmp") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_name = temp_file.name
                msg_dict["media_files"].append(temp_file_name)
                print(f"Temp file created: {temp_file_name}")
    return msg_dict



def clearTempFiles(file_paths: list):
    for file_path in file_paths:
            Path(file_path).unlink() 
    
    
async def parallelApiPosting(funcs_to_call: list, posting_data: dict):
    if posting_data:
       await asyncio.gather(*funcs_to_call)
       

def envVarInFile(vars_to_check: KeysView[str], file_path: Path) -> bool:
    if file_path.exists():
        with open(file_path, 'r') as file:
            file_content = file.read() 
        return all(env_var in file_content for env_var in vars_to_check)


def tempByteToFilesCreator(byte_files: list, media_type: str) -> list:
    if len(byte_files) == 0:
        return []
    media_extensions = {
        "image": ".jpeg",  
        "video": ".mp4",
        }
    temp_media_file_paths = []  
    for byte_data in byte_files:
        with tempfile.NamedTemporaryFile(suffix=media_extensions[media_type], delete=False) as temp_file:
            temp_file.write(byte_data)  
            temp_file.flush()  
            temp_file_name = temp_file.name  
            temp_media_file_paths.append(temp_file_name) 
    return temp_media_file_paths 

def downloadChromeDriver():
    from webdriver_manager.chrome import ChromeDriverManager
    import shutil
    webdriver_path = Path(os.getenv("CHROME_WEBDRIVER"))
    full_driver_path = webdriver_path 
    print(webdriver_path)
    if full_driver_path.exists():
        print(f"WebDriver already exists at: {full_driver_path}")
    else:
        print("Downloading WebDriver...")
        default_driver_path = ChromeDriverManager().install()
        shutil.move(default_driver_path, full_driver_path)
        print(f"WebDriver downloaded and moved to: {full_driver_path}")

def ensureEnvVars():
    BASE_DIR = Path(__file__).resolve().root
    env_file = Path('.env')
    env_paths = {
        "BASE_DIR": BASE_DIR,
        "MY_PIPE_PATH": BASE_DIR / "DataStreamPipe.fifo",  
        "IMAGE_DIR": BASE_DIR / "saved_images",            
        "VID_DIR": BASE_DIR / "saved_videos",              
        "METADATA_FILE": BASE_DIR / "data" / "metadata.json",
        "CHROME_WEBDRIVER": BASE_DIR /"data"/ "chrome_webdriver",
        "CHROME_USER_DATA": BASE_DIR /"data"/ "chrome_user_data"      
    }
    if not envVarInFile(env_paths.keys(), env_file):
        with open(env_file, 'a') as update_env_vars:
            update_env_vars.write("\n""\n".join([
                "",  
                "# base dir and named pipe path\n"
            ]))
            for key, value in env_paths.items():
                update_env_vars.write(f"{key} = '{str(value)}'\n")
