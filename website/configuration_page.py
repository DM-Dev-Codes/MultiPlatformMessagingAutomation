import streamlit as st
from pathlib import Path
from common.sqlwriter import writeConstantMessages, writeGroupNames, eraseGroupName, readGroupNamesDB


BASE_DIR = Path(__file__).resolve().parent.parent
env_file_path = BASE_DIR / "checking.env"


env_paths = {
    "BASE_DIR": BASE_DIR,
    "MY_PIPE_PATH": BASE_DIR / "DataStreamPipe.fifo",  
    "IMAGE_DIR": BASE_DIR / "saved_images",            
    "VID_DIR": BASE_DIR / "saved_videos",              
    "METADATA_FILE": BASE_DIR / "data" / "metadata.json",
    "CHROME_WEBDRIVER": BASE_DIR / "data" / "chrome_webdriver",
    "CHROME_USER_DATA": BASE_DIR / "data" / "chrome_user_data"
}

config_mappings = {
    "Telegram Configuration": {
        "TELEGRAM_BOT_TOKEN": "password",
        "TELEGRAM_BOT_USERNAME": "text",
        "TELEGRAM_GROUP_ID": "text"
    },
    "Telethon API Configuration": {
        "TELEGRAM_API_ID": "text",
        "TELEGRAM_API_HASH": "password"
    },
    "SQL Database Configuration": {
        "SQL_HOST": "text",
        "SQL_USER": "text",
        "SQL_PASSWORD": "password",
        "SQL_DATABASE": "text"
    },
    "Twitter API Configuration": {
        "TWITTER_BEARER_TOKEN": "password",
        "TWITTER_CONSUMER_KEY": "password",
        "TWITTER_CONSUMER_SECRET": "password",
        "TWITTER_ACCESS_TOKEN": "password",
        "TWITTER_ACCESS_TOKEN_SECRET": "password",
        "TWITTER_CLIENT_SECRET": "password",
        "TWITTER_CLIENT_ID": "text"
    }
}

def saveConfiguration(telegram_bot_token, telegram_bot_username, telegram_group_id,
                       telegram_api_id, telegram_api_hash, sql_host, sql_user, sql_password,
                       sql_database, twitter_bearer_token, twitter_consumer_key,
                       twitter_consumer_secret, twitter_access_token, twitter_access_token_secret,
                       twitter_client_secret, twitter_client_id):
    
    config_dict = {
        "TOKEN": telegram_bot_token,
        "BOT_USERNAME": telegram_bot_username,
        "GROUP_ID": telegram_group_id,
        "API_ID": telegram_api_id,
        "TELEGRAM_API_HASH": telegram_api_hash,
        "HOST": sql_host,
        "USER": sql_user,
        "PASSWORD": sql_password,
        "DATABASE": sql_database,
        "BEARER_TOKEN": twitter_bearer_token,
        "CONSUMER_KEY": twitter_consumer_key,
        "CONSUMER_SECRET": twitter_consumer_secret,
        "ACCESS_TOKEN": twitter_access_token,
        "ACCESS_TOKEN_SECRET": twitter_access_token_secret,
        "CLIENT_SECRET": twitter_client_secret,
        "CLIENT_ID": twitter_client_id
    }


    with open(env_file_path, "w") as f:
        for key, value in config_dict.items():
            f.write(f"{key} = '{value}'\n")

    with open(env_file_path, "a") as f:
        f.write("\n# Base directories and paths\n")
        for key, value in env_paths.items():
            f.write(f"{key} = '{str(value)}'\n")
    
    st.success("Configuration saved!")



def getTelegramConfig():
    st.subheader("Telegram Configuration")
    telegram_bot_token = st.text_input("Telegram Bot Token", type="password")
    telegram_bot_username = st.text_input("Telegram Bot Username")
    telegram_group_id = st.text_input("Telegram Group ID")
    return telegram_bot_token, telegram_bot_username, telegram_group_id


def getTelethonConfig():
    st.subheader("Telethon API Configuration")
    telegram_api_id = st.text_input("Telethon API ID")
    telegram_api_hash = st.text_input("Telethon API Hash", type="password")
    return telegram_api_id, telegram_api_hash


def getSqlConfig():
    st.subheader("SQL Database Configuration")
    sql_host = st.text_input("SQL Host")
    sql_user = st.text_input("SQL User")
    sql_password = st.text_input("SQL Password", type="password")
    sql_database = st.text_input("SQL Database")
    return sql_host, sql_user, sql_password, sql_database


def getTwitterConfig():
    st.subheader("Twitter API Configuration")
    twitter_bearer_token = st.text_input("Twitter Bearer Token", type="password")
    twitter_consumer_key = st.text_input("Twitter Consumer Key", type="password")
    twitter_consumer_secret = st.text_input("Twitter Consumer Secret", type="password")
    twitter_access_token = st.text_input("Twitter Access Token", type="password")
    twitter_access_token_secret = st.text_input("Twitter Access Token Secret", type="password")
    twitter_client_secret = st.text_input("Twitter Client Secret", type="password")
    twitter_client_id = st.text_input("Twitter Client ID")
    return twitter_bearer_token, twitter_consumer_key, twitter_consumer_secret, \
           twitter_access_token, twitter_access_token_secret, twitter_client_secret, twitter_client_id
           
def getWhatsappConfig(update_flag=False):
    st.subheader("WhatsApp Configuration" if not update_flag else "Manage WhatsApp Groups")
    
    # Option to add or delete groups
    action = st.selectbox("Choose an action", ["Add Group", "Delete Group"])
    
    if action == "Add Group":
        whatsapp_group_id = st.text_input("Enter WhatsApp Group Name (separated by whitespace, must match exact group name case sensitive)")
        if whatsapp_group_id:
            group_names = whatsapp_group_id.split()
            writeGroupNames(group_names)
            st.success("Group(s) added successfully!")
    
    elif action == "Delete Group":
        group_names = readGroupNamesDB()  
        if group_names: 
            group_to_delete = st.selectbox("Select a group to delete", group_names)
            if group_to_delete:
                confirm_delete = st.button(f"Delete {group_to_delete}")
                if confirm_delete:
                    eraseGroupName(group_to_delete)  
                    st.success(f"Group '{group_to_delete}' deleted successfully!")
        else:
            st.warning("No groups available to delete.")


def getMysqlConfig():
    st.subheader("MySQL Database Configuration")
    mysql_database = st.text_input("MySQL Database Name")
    return mysql_database

def firsConfigSetUpForm():
    telegram_bot_token, telegram_bot_username, telegram_group_id = getTelegramConfig()
    telegram_api_id, telegram_api_hash = getTelethonConfig()
    sql_host, sql_user, sql_password, sql_database = getSqlConfig()
    twitter_bearer_token, twitter_consumer_key, twitter_consumer_secret, \
    twitter_access_token, twitter_access_token_secret, twitter_client_secret, twitter_client_id = getTwitterConfig()
    whatsapp_group_id = getWhatsappConfig()  # New field for WhatsApp
    boosting_message_coffee = st.text_area("Boosting Message", "Default Coffee Message")
    boosting_message = st.text_area("Boosting Message", "Default Boosting Message")
   
    
    with st.form("config_form"):
        submitted = st.form_submit_button("Save Configuration")
        if submitted:
            saveConfiguration(telegram_bot_token, telegram_bot_username, telegram_group_id,
                               telegram_api_id, telegram_api_hash, sql_host, sql_user, sql_password,
                               sql_database, twitter_bearer_token, twitter_consumer_key,
                               twitter_consumer_secret, twitter_access_token, twitter_access_token_secret,
                               twitter_client_secret, twitter_client_id)
            updateConstantMessage("coffee", boosting_message_coffee)
            updateConstantMessage("boosting", boosting_message)
            writeGroupNames(whatsapp_group_id)


def updatTelegramConfig():
    telegram_bot_token, telegram_bot_username, telegram_group_id = getTelegramConfig()
    updated_config = {
        "TELEGRAM_BOT_TOKEN": telegram_bot_token,
        "TELEGRAM_BOT_USERNAME": telegram_bot_username,
        "TELEGRAM_GROUP_ID": telegram_group_id
    }
    if st.button("Save Telegram Configuration"):
        update_env_variables(updated_config)
        st.success("Telegram Configuration Updated!")


def updateTelethonConfig():
    telegram_api_id, telegram_api_hash = getTelethonConfig()
    updated_config = {
        "TELEGRAM_API_ID": telegram_api_id,
        "TELEGRAM_API_HASH": telegram_api_hash
    }
    if st.button("Save Telethon Configuration"):
        update_env_variables(updated_config)
        st.success("Telethon API Configuration Updated!")


def updateSqlConfig():
    sql_host, sql_user, sql_password, sql_database = getSqlConfig()
    updated_config = {
        "SQL_HOST": sql_host,
        "SQL_USER": sql_user,
        "SQL_PASSWORD": sql_password,
        "SQL_DATABASE": sql_database
    }
    if st.button("Save SQL Configuration"):
        update_env_variables(updated_config)
        st.success("SQL Database Configuration Updated!")


def updateTwitterConfig():
    twitter_bearer_token, twitter_consumer_key, twitter_consumer_secret, \
    twitter_access_token, twitter_access_token_secret, twitter_client_secret, twitter_client_id = getTwitterConfig()
    updated_config = {
        "TWITTER_BEARER_TOKEN": twitter_bearer_token,
        "TWITTER_CONSUMER_KEY": twitter_consumer_key,
        "TWITTER_CONSUMER_SECRET": twitter_consumer_secret,
        "TWITTER_ACCESS_TOKEN": twitter_access_token,
        "TWITTER_ACCESS_TOKEN_SECRET": twitter_access_token_secret,
        "TWITTER_CLIENT_SECRET": twitter_client_secret,
        "TWITTER_CLIENT_ID": twitter_client_id
    }
    if st.button("Save Twitter Configuration"):
        update_env_variables(updated_config)
        st.success("Twitter Configuration Updated!")

def updateConstantMessage(message_type=None):
    if message_type == "Coffee Message":
        coffee_message = st.text_area("Coffee Message", "Default Coffee Message")
        if st.button("Save Coffee Message"):
            writeConstantMessages("boosting", coffee_message)
            st.success("Coffee Message Updated!")
    
    elif message_type == "Boosting Message":
        boosting_message = st.text_area("Boosting Message", "Default Boosting Message")
        if st.button("Save Boosting Message"):
            writeConstantMessages("boosting", boosting_message)
            st.success("Boosting Message Updated!")




def configurationPage():
    st.title("Configuration")
    selected_group = st.selectbox("Select a group", ["First time config", "Update Information"])
    if selected_group == "First time config":
        firsConfigSetUpForm()
    elif selected_group == "Update Information":
        update_section = st.selectbox("Select section to update", [
            "Telegram Configuration", "Telethon API Configuration", 
            "SQL Database Configuration", "Twitter API Configuration", 
            "Coffee Message", "Boosting Message","Whatsapp Groups"
        ])
        update_functions = {
            "Telegram Configuration": updatTelegramConfig,
            "Telethon API Configuration": updateTelethonConfig,
            "SQL Database Configuration": updateSqlConfig,
            "Twitter API Configuration": updateTwitterConfig,
            "Coffee Message": lambda: updateConstantMessage("Coffee Message"),
            "Boosting Message": lambda: updateConstantMessage("Boosting Message"),
            "Whatsapp Groups": lambda: getWhatsappConfig(update_flag=True)
        }
        if update_section in update_functions:
            update_functions[update_section]()


def readEnvFileForUpdate():
    env_dict = {}
    with open(env_file_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                env_dict[key.strip()] = value.strip().strip("'")
    return env_dict


def saveUpdatedConfig(updated_config):
    with open(env_file_path, 'w') as f:
        for key, value in updated_config.items():
            f.write(f"{key} = '{value}'\n")
    st.success("Configuration updated!")


def update_env_variables(new_config):
    current_config = readEnvFileForUpdate()
    updated_config = {key: value for key, value in new_config.items() if value}
    current_config.update(updated_config)
    saveUpdatedConfig(current_config)
        
        