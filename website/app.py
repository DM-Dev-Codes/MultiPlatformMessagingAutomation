import streamlit as st
from streamlit_option_menu import option_menu
from enum import Enum
from website.configuration_page import configurationPage
# from website.account import AccountPage
from website.home import HomePage
from website.send_message import SendMessagePage
from website.schedulingtasks import schedulingTasksPage


class MenuOptions(Enum):
    HOME = "Home"
    # ACCOUNT = "Account"
    SEND_MESSAGE = "Send Message"
    CONFIGURATION = "Configuration"  
    SCHEDULING = "Scheduling"  

class MultiApp:
    def __init__(self):
        self.apps = []
        
    def addApp(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
             })
        
    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title="Main Menu",
                options=[option.value for option in MenuOptions],
                icons=["house", "user", "paper-plane", "file-text", "info-circle"],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important", "background-color": 'black'},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
            page_functions = {
                MenuOptions.HOME.value: HomePage,
                # MenuOptions.ACCOUNT.value: AccountPage,
                MenuOptions.SEND_MESSAGE.value: SendMessagePage,
                MenuOptions.CONFIGURATION.value: configurationPage,  
                MenuOptions.SCHEDULING.value: schedulingTasksPage,  
            }
        if app in page_functions:
            page_functions[app]() 
             
             
if __name__ == "__main__":
    multi_app = MultiApp()
    multi_app.run()
                
     
