import streamlit as st
from common.utils import bundleMessageForProcess
from common.group_ids import GroupID
from pipe_manager import NamedPipeManager
from openai import OpenAI
import time


def SendMessagePage():
    pipe_instance = NamedPipeManager()
    st.title("Send Message Page")
    group_name_to_id_map = GroupID.nameValuePairMap()
    selected_group = st.selectbox("Select a group", list(group_name_to_id_map.keys()))
    message = st.text_area(label="Type Message here")
    uploaded_files = st.file_uploader(label="Select Media", type=["jpeg", "png", "mp4"], accept_multiple_files=True)
    corrected_message = None
    if st.button(label="AI Check"):
        corrected_message = gpt(message)
        if corrected_message:
            st.text_area("Corrected Message", corrected_message, height=150)
    if st.button(label="Send Message"):
        message_to_send = corrected_message if corrected_message else message
        bundled_msg_for_sending = bundleMessageForProcess(group_name_to_id_map[selected_group], message_to_send, uploaded_files)
        print(f" this is bundled chat: {bundled_msg_for_sending}")
        pipe_instance = NamedPipeManager.getNamedPipe()
        pipe_instance.operateOnPipe("write", bundled_msg_for_sending)
        print(f"this is the send message page with the bundled messsage in website.send_message: {bundled_msg_for_sending}")





def gpt(message):
    from openai import OpenAI
    import os
    key = os.getenv("GPT_API")
    client = OpenAI(api_key=key)
    messages = [
        {"role": "system", "content": "You are a helpful assistant skilled in text corrections."},
        {"role": "user", "content": f"""
        Please correct the spelling errors in the following text while maintaining accuracy for:
        1. Israeli towns (spelled in English),
        2. Arab towns (spelled in English), and
        3. Worldwide politicians.
        
        Text: {message}
        
        Return only the corrected text:
        """}
    ]

    retries = 5  # Number of retry attempts
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            corrected_message = response.choices[0].message.content
            print(f"GPT Response: {corrected_message}")
            return corrected_message
        except Exception as e:
            print(f"Error during GPT API call: {e}")
            if i < retries - 1:  # Avoid sleeping after the last retry
                wait_time = 2 ** i  # Exponential backoff: 2^i seconds
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
