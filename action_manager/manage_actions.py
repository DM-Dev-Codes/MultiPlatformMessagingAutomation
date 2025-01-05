import os
import asyncio
import logging
from dotenv import load_dotenv
from common.sqlwriter import *
from telethon.tl.types import Message
from common.utils import parseMessageMetadata, jsonWriter, clearTempFiles, parallelApiPosting
from api.tweets import createTweet
from bot.bot import *
from api.tweets import *
from common.sql import *
from common.utils import *
from pipe_manager import NamedPipeManager

pipe_instance = None

def startPipe():
    global pipe_instance
    logging.debug("Initializing NamedPipeManager...")
    pipe_manager = NamedPipeManager()
    pipe_manager._initialize()
    pipe_instance = pipe_manager.getNamedPipe()
    logging.debug("NamedPipeManager initialized and pipe instance assigned.")

load_dotenv()

async def listenForNamedPipeContent():
    logging.debug("Starting to listen for named pipe content...")
    startPipe()
    pipe_path = os.getenv("MY_PIPE_PATH")
    try:
        while True:  
            pipe_content = pipe_instance.operateOnPipe("read")
            if pipe_content:
                logging.debug(f"Data detected in the pipe at: {pipe_path}")
                await launchConcurrentTasks(pipe_content)
            else:
                logging.debug("No data in the pipe. Sleeping for 1 second...")
                await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.debug("Process interrupted by user.")
        pass
    except Exception as e:
        logging.error(f"Error occurred while reading from the pipe: {e}")
        
async def sequentialTasks():
    logging.debug("Starting sequential tasks...")
    try:
        db_success_flag = writeMsgDb()
        if db_success_flag:
            logging.debug("Message successfully written to the database. Proceeding to create tweet...")
            createTweet()
            logging.debug("Calling autoWhatsappGroupMessaging function...")
            from whatsapp_web.whatsapp_selenium import autoWhatsappGroupMessaging
            autoWhatsappGroupMessaging()
        else:
            logging.warning("Failed to write message to the database.")
    except Exception as e:
        logging.error(f"Error in sequential tasks: {e}")


async def launchConcurrentTasks(pipe_content):
    logging.debug("Launching concurrent tasks based on pipe content...")
    try:
        bot_response, media_tmp_files = await botMain(pipe_content)
        logging.debug(f"Bot response: {bot_response}, Temporary files: {media_tmp_files}")
        if bot_response:
            logging.debug("Bot response is a valid Message instance.")
            parsed_msg_metadata = parseMessageMetadata(bot_response, media_tmp_files)
            logging.debug(f"Parsed message metadata: {parsed_msg_metadata}")
            if parsed_msg_metadata:
                logging.debug("Parsed metadata successfully, attempting to save...")
                saving_metadata_flag = jsonWriter(parsed_msg_metadata, os.getenv("METADATA_FILE"))
                if saving_metadata_flag:
                    logging.debug("Metadata saved successfully. Proceeding with sequential tasks...")
                    await sequentialTasks()
                else:
                    logging.warning("Failed to save metadata.")
            else:
                logging.warning("No valid metadata parsed.")
        else:
            logging.warning("Bot response is not a valid Message instance.")
    except Exception as e:
        logging.error(f"Error in launching concurrent tasks: {e}")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.debug("Starting main process...")
    asyncio.run(listenForNamedPipeContent())
