import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()



class NamedPipeManager:
    pipe_name = os.getenv("MY_PIPE_PATH")
    pipe_path = Path(os.getenv("BASE_DIR")) / pipe_name
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if not self.pipe_path.exists():
            os.mkfifo(str(self.pipe_path))
            print(f"Named pipe created at: {self.pipe_path}")
        else:
            print(f"Named pipe already exists at: {self.pipe_path}")
            
    @staticmethod
    def getNamedPipe(): 
        return NamedPipeManager._instance
             
    
    def operateOnPipe(self, file_action: str, data=None):
        logging.debug(f"Attempting to {file_action} to/from the pipe at: {self.pipe_path}")
        
        action_mode = {"write": "w", "read": "r"}
        
        if file_action in action_mode:
            try:
                with open(self.pipe_path, action_mode[file_action]) as pipe_file:
                    if file_action == "write":
                        json.dump(data, pipe_file, indent=4)
                        pipe_file.flush()
                        logging.debug(f"Successfully written to the pipe: {data}")  
                    elif file_action == "read":
                        read_data = pipe_file.read()
                        if read_data:  
                            read_data = json.loads(read_data)
                            logging.debug(f"Successfully read from the pipe: {read_data}") 
                            return read_data
                        else:
                            logging.warning("Pipe is empty. No data read.")
                    else:
                        logging.error("Invalid action specified. Use 'write' or 'read'.")
            except FileNotFoundError:
                logging.error(f"Error: Named pipe {self.pipe_path} not found.")
            except json.JSONDecodeError as json_error:
                logging.error(f"JSON decode error: {json_error}")
            except Exception as e:
                logging.error(f"Error accessing pipe: {e}")
        else:
            logging.error("Invalid action specified. Use 'write' or 'read'.")

#for wildcard import *
__all__ = ['PipeInstance']


