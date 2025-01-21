import streamlit as st  
from auth.auth_manager import AuthManager
from auth.db_manager import DatabaseManager
from dashboards.userdashboard import render_user_dashboard 
from mongo.chatdb import MongoDb
from dashboards.admindashboard import show_admin_dashboard

# Initialize database and authentication manager
try:
    db = DatabaseManager("users.db")
    auth = AuthManager(db)
except Exception as e:
    st.error(f"Failed to initialize database or auth manager: {e}")

# Initialize session state
if "mongo" not in st.session_state:
    try:
        st.session_state.mongo = MongoDb()
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.messages = []

def main():
    st.title("Financial Chatbot")

    # Check login state
    if st.session_state.logged_in:
        if st.session_state.role == "Admin":
            show_admin_dashboard(logout)
        elif st.session_state.role == "User":
            try:
                query, response,tokens = render_user_dashboard(st.session_state.username, logout)
                if query:
                    st.session_state.mongo.add_message_to_chat_session(
                        st.session_state.current_session, 'user', query)
                    st.session_state.mongo.add_message_to_chat_session(
                        st.session_state.current_session, 'assistant', response)
                    st.session_state.mongo.add_tokens(st.session_state.username,tokens)
            except Exception as e:
                st.error(f"Error in rendering user dashboard: {e}")
    else:
        menu = ["Admin Login", "User Login", "Sign Up"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Admin Login":
            admin_login_page()
        elif choice == "User Login":
            user_login_page()
        elif choice == "Sign Up":
            signup_page()

def admin_login_page():
    st.subheader("Admin Login")
    username = st.text_input("Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.session_state.username = "Admin"
                st.success("Admin logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")
        except Exception as e:
            st.error(f"Error during admin login: {e}")

def user_login_page():
    st.subheader("User Login")
    gmail = st.text_input("Gmail")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            username = auth.login(gmail, password)
            if username:
                st.session_state.logged_in = True
                st.session_state.role = "User"
                st.session_state.username = username
                st.success("User logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid email or password")
        except Exception as e:
            st.error(f"Error during user login: {e}")

def signup_page():
    st.subheader("Sign Up")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        try:
            validation_msg = auth.validate_password(password)
            if validation_msg:
                if auth.signup(username, email, password):
                    try:
                        st.session_state.mongo.create_new_user(username, email)
                        st.session_state.mongo.create_new_chat_session(username, "default")
                        st.success("Account created successfully! You can now log in.")
                    except Exception as e:
                        st.error(f"Error creating chat session: {e}")
                else:
                    st.error("Username or email already exists.")
            else:
                st.error(validation_msg)
        except Exception as e:
            st.error(f"Error during sign-up: {e}")

def logout():
    try:
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.messages = []
        st.rerun()
    except Exception as e:
        st.error(f"Error during logout: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
