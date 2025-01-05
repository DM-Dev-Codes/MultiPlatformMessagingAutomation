# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials 
# from firebase_admin import auth
# from dotenv import load_dotenv
# import os
# load_dotenv()

# # One-time initialization of Firebase
# if not firebase_admin._apps:
#     fire_base_creds = credentials.Certificate(os.getenv('FIREBASE_CONFIG_PATH'))
#     firebase_admin.initialize_app(fire_base_creds)

# def AccountPage():
#     if st.session_state.signedout:
#         st.title(f"Welcome Back, {st.session_state.username}!")
#     else:
#         st.title("Let's Get You :violet[Signed In!]")
#     st.session_state.setdefault("username", "")
#     st.session_state.setdefault("user_email", "")
#     st.session_state.setdefault("signedout", False)
#     st.session_state.setdefault("signout", False)
#     if not st.session_state.signedout:
#         login_option = st.selectbox("Choose an option", ["Login", "Sign up"])
#         if login_option == "Login":
#             user_email, user_password, _ = userCredsForm(new_account=False)
#             st.button("Login", on_click=lambda: authUserLogin(user_email))
#         else:
#             user_email, user_password, username = userCredsForm(new_account=True)
#             if  st.button("Create my account"):
#                 new_user = auth.create_user(email=user_email, password=user_password, uid=username)
#                 st.success("Account created successfully!")
#                 st.markdown("Please Login using your email and password")
#                 st.balloons()
#     else:
#         st.text(f"Name: {st.session_state.username}\nEmail ID: {st.session_state.user_email}")
#         st.button("Sign Out", on_click=setSignOutState)
           
# def userCredsForm(new_account=False):
#     user_email = st.text_input("Email Address")
#     user_password = st.text_input("Password", type="password")
#     username = st.text_input("Enter your unique username") if new_account else " "
#     return user_email, user_password, username

# def authUserLogin(user_email: str):
#     try:
#         user = auth.get_user_by_email(user_email)
#         st.write("Login succesful")
#         st.session_state.username = user.uid
#         st.session_state.user_email= user.email
#         st.session_state.signedout = True
#     except Exception as login_error:
#         st.warning(f"Login Failed: {login_error}")
        
# def setSignOutState():
#     st.session_state.signout = False
#     st.session_state.signedout = False   
#     st.session_state.username = ""
#     st.session_state.user_email = ""
        
        
# if "signedout" not in st.session_state:
#     st.session_state.signedout = False
# if "signout" not in st.session_state:
#     st.session_state.signout = False
    


    