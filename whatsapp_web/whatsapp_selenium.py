from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import os
import random
from common.utils import tempByteToFilesCreator
from common.sqlwriter import readGroupNamesDB, parseQuery
import logging


# def randomWait(min_wait=1, max_wait=3):
#     time.sleep(random.uniform(min_wait, max_wait))



def autoWhatsappGroupMessaging():
    debugging = True
    user_data_path = os.getenv('CHROME_USER_DATA')
    driver_path = Path(os.getenv("CHROME_WEBDRIVER"))
    service = Service(str(driver_path))
    chrome_options = Options()
    user_data_dir = Path(user_data_path)
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")

    if debugging:
        chrome_options.add_experimental_option("detach", True)
    else:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://web.whatsapp.com/")
    
    groups = readGroupNamesDB()
    text, media_files = bundleMsgForWhatsapp()
    # media_files = [media_files[0]] if media_files else [] 
    groups =["Documents"]
    
    
    try:
        for group_name in groups:
            search_box = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            search_box.click()
            search_box.clear()
            search_box.send_keys(group_name)
            # time.sleep(2)
            # randomWait(1,2)
            group = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{group_name}"]'))
            )
            group.click()
            # time.sleep(2)
            if media_files:
                plus_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-hidden='true'][data-icon='plus']"))
                )
                plus_button.click()
                # randomWait(2,3)
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                for file_path in media_files:
                    absolute_path = Path(file_path).resolve()
                    file_input.send_keys(str(absolute_path))
                time.sleep(2)
                message_box = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="undefined"]'))
                )
                message_box.click()
                message_box.send_keys(text)
                message_box.send_keys(Keys.ENTER)
            else:
                message_box = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                message_box.click()
                message_box.send_keys(text)
                message_box.send_keys(Keys.ENTER)
            print(f"Message and media sent to group: {group_name}")
        time.sleep(3)
    except Exception as e:
        print(f"An error occurred: {e}")
        
    # finally:
    #     debugger = False
    #     if not debugger:
    #         driver.quit()
        
def bundleSqlMsg():
    message_to_send = parseQuery()
    text_content = message_to_send.get("text")
    image_bytes_files = message_to_send.get("images_as_bytes", [])
    video_bytes_files = message_to_send.get("videos_as_bytes",[])
    temp_media_img = tempByteToFilesCreator(image_bytes_files, "image")
    temp_media_vid = tempByteToFilesCreator(video_bytes_files, "video")
    media_files = temp_media_img + temp_media_vid
    logging.debug(f"proccesed media files foer hwtasapp{media_files}")
    return text_content, media_files


def bundleMsgForWhatsapp():
    text, media = bundleSqlMsg()
    return text, [media[0]] if media else []
    # return element as list not as standalone value

def getMediaTempFiles(media_file_paths: list):
    if media_file_paths:
        return media_file_paths
    return []  


# if __name__ == "__main__":
#      autoWhatsappGroupMessaging()