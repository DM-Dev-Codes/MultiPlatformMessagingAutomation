# Standard Library Imports
import os
import asyncio
import logging
from pathlib import Path
from typing import  List
from dotenv import load_dotenv
from telethon import events
from telethon.sync import TelegramClient
# from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from pipe_manager import NamedPipeManager
from common.utils import parseMessageMetadata,  jsonWriter, clearTempFiles, parallelApiPosting
from common.sqlwriter import writeMsgDb
from api.tweets import createTweet
# Loading environment variables
load_dotenv()


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# BASE_DIR = Path(os.getenv("BASE_DIR"))
IMAGE_DIR = os.getenv("IMAGE_DIR")
VIDEO_DIR =  os.getenv("VIDEO_DIR")
METADATA_FILE = os.getenv("METADATA_FILE")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TOKEN")

client = None
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  


async def runBot():
    global client
    if not client:
        client = TelegramClient('bot', API_ID, API_HASH)
        try:
            await client.start(bot_token=TOKEN )
            logger.debug("Bot is running...")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        else:
            return


async def shutdownBot():
    global client
    if client:
        try:
            logger.debug("Shutting down bot...")
            await client.disconnect()  
            logger.debug("Bot has been disconnected.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
                       
           
async def uploadMediaFiles(media_for_upload: List[str], telegram_client) -> List:
    if media_for_upload:
        tasks = [telegram_client.upload_file(file_path) for file_path in media_for_upload]
        return await asyncio.gather(*tasks)
    return []

async def sendMessageToGroup(bundled_msg: dict) -> bool:
    global client
    try:
        group_id = bundled_msg.get("group_name",None)
        text_content = bundled_msg.get("text_content",None)
        media_files = bundled_msg.get("media_files",None)
        logger.debug(f"Sending message to group: {group_id}, Text: {text_content}, Media: {media_files}")
        if media_files:
            uploaded_media = await uploadMediaFiles(media_files, client)
            if uploaded_media:
                #send file function cant handle large text
                # sent_msg = await client.send_file(group_id, uploaded_media, caption=text_content, force_document=False)
                sent_msg = await client.send_message(group_id, text_content, file=uploaded_media)
                # clearTempFiles(media_files)
            else:
                return None, None
        else:
            sent_msg = await client.send_message(group_id, text_content)
        logger.debug(f"Sent message type: {type(sent_msg)}")
        return (sent_msg, media_files) if sent_msg else None
    except Exception as e:
        logger.error(f"Failed to send message to group {group_id}: {e}")
        return None, None


async def botMain(pipe_object_content):
    global client
    try:
        logger.debug("Starting botMain function.")
        await runBot()
        logger.debug("Bot initialized.")
        if client:
            logger.debug("Client is connected. Checking pipe content.")
            pipe_content = pipe_object_content
            if pipe_content:
                logger.debug(f"Pipe content found: {pipe_content}")
                result = await sendMessageToGroup(pipe_content)
                if result:
                    # await shutdownBot()
                    return result
                logger.debug(f"Message sent to group with content: {pipe_content}")
            else:
                logger.warning("No pipe content found.")
        else:
            logger.error("Client is not connected.")

    except Exception as e:
        logger.error(f"An error occurred in botMain: {e}")
