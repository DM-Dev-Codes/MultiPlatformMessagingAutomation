import logging
import tempfile
from common.sqlwriter import parseQuery  
from api.tweetApi import TwitterAPI  

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def verifyCreds():
    client = TwitterAPI.getClient()
    try:
        if client.get_me():
         return True
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
    return False

def uploadTwitterMedia(media_bytes: list, media_type: str) -> None:
    api = TwitterAPI.getApi()
    media_ids = []
    if not media_bytes:
        logging.warning("No media bytes provided for upload.")
        return []
    for bytes in media_bytes:
        if bytes is None or len(bytes) == 0:
            logging.warning("Skipping empty or None media of type")
            continue
        with tempfile.NamedTemporaryFile(suffix=media_type, delete=True) as temp_file:
            temp_file.write(bytes)
            temp_file.flush() 
            media_upload_id = api.media_upload(filename=temp_file.name).media_id_string
            logging.info(f"this is the media uplaod id {media_upload_id }")
            media_ids.append(media_upload_id) 
    logging.info(f"this is the media uplaod ids lost {media_ids}")
    return media_ids

              
def getMediaIds():
    query_data = parseQuery() 
    tweet_text = query_data.get("text")
    media_data = {
        'images_as_bytes': (query_data.get('images_as_bytes'), ".jpeg"),
        'videos_as_bytes': (query_data.get('videos_as_bytes'), ".mp4")
    }
    all_media_ids = []
    for _, (media_bytes, file_extension) in media_data.items():
        if media_bytes: 
            media_ids = uploadTwitterMedia(media_bytes, file_extension)
            all_media_ids.extend(media_ids)
    logging.info(f"All media IDs: {all_media_ids}")
    return all_media_ids, tweet_text



#create and post tweet using v2 endpoint
def createSingleTweet(text: str, media_ids_list=None):
    client = TwitterAPI.getClient()
    try:
        if media_ids_list:
            client.create_tweet(text=text, media_ids=media_ids_list)
        else:
         client.create_tweet(text=text)
    except Exception as issue_creating_tweet:
        logging.error(f"Error creating tweet: {issue_creating_tweet}")
    
def createTweetThread(media_ids_list: list, text: str) -> None: 
    client = TwitterAPI.getClient()
    thread_id  = None
    for index, media_id_group in enumerate(media_ids_list):
        try:
            if index == 0:
                initial_tweet = client.create_tweet(text=text, media_ids=media_id_group)
                thread_id = initial_tweet.data["id"]
            else:
                response_tweet = client.create_tweet(text=None, media_ids=media_id_group, in_reply_to_tweet_id=thread_id)
                thread_id = response_tweet.data["id"]
        except Exception as issue_creating_tweets:
            logging.error(f"Error creating tweet thread: {issue_creating_tweets}")

            
def createTweet():
    split_ids = []
    media_ids, text = getMediaIds()
    logging.info(f"Tweet media ids: {media_ids}")
    if media_ids or text:
        if len(media_ids) > 4:
            for i in range(0, len(media_ids), 4):
             split_ids.append(media_ids[i : i + 4])
            createTweetThread(split_ids, text)
        else:
            createSingleTweet(text, media_ids)
    else:
        logging.info("Failed to create single tweet/tweet thread")
        