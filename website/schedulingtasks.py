import streamlit as st

def handleMessageScheduling(action, message_type=None):
    if action == "Create New Message":
        if message_type:
            st.subheader(f"Create {message_type}")
            with st.form(f"create_{message_type.lower()}_message_form"):
                message = st.text_area(f"Enter your {message_type.lower()} message", "Type your message here...")
                schedule_option = st.radio("Select how to schedule the message", ["Every few hours", "At a specific time"])
                if schedule_option == "Every few hours":
                    interval_hours = st.number_input("How many hours between each message?", min_value=1, step=1)
                elif schedule_option == "At a specific time":
                    message_time = st.time_input("Select time to send message", value=None)
                submitted = st.form_submit_button(f"Create {message_type}")
                if submitted:
                    st.write(f"{message_type} scheduled: '{message}'")
                    if schedule_option == "Every few hours":
                        st.write(f"Message will be sent every {interval_hours} hours.")
                    elif schedule_option == "At a specific time":
                        st.write(f"Message will be sent at: {message_time}")

    elif action == "Adjust Existing Message":
        message_type = st.selectbox("Select Message to Adjust", ["Select a message", "Coffee Message", "Boosting Message"])
        if message_type != "Select a message":
            st.subheader(f"Adjust Existing {message_type} Schedule")
            adjust_option = st.radio("How would you like to adjust?", ["By Hours", "Set a Specific Time"])
            with st.form("adjust_message_form"):
                if adjust_option == "By Hours":
                    interval_hours = st.number_input("How many hours between each message?", min_value=1, step=1)
                    st.write(f"Message will now be sent every {interval_hours} hours.")
                elif adjust_option == "Set a Specific Time":
                    message_time = st.time_input("Select time to send message", value=None)
                    st.write(f"Message will now be sent at: {message_time}")
                adjust_submitted = st.form_submit_button("Adjust Message")
                if adjust_submitted:
                    st.write(f"Adjusting schedule for: {message_type}")

def schedulingTasksPage():
    st.title("Schedule Regular Messages")
    action = st.selectbox("What would you like to do?", ["Select an action", "Create New Message", "Adjust Existing Message"])
    if action == "Create New Message":
        message_type = st.selectbox("Select Message Type", ["Select a message", "Coffee Message", "Boosting Message"])
        if message_type != "Select a message":
            handleMessageScheduling(action, message_type)
    elif action == "Adjust Existing Message":
        handleMessageScheduling(action)
