import streamlit as st
import pandas as pd
def get_user_data():
    #Fetch user data from the users collection
    users = list(st.session_state.mongo.users.find())
    user_data = []

    #Loop through each user and fetch their chat details
    for user in users:
        user_id = user.get("_id")
        email = user.get("gmail")
        chat_ids = user.get("chat_history", [])  # List of chat session ids for the user
        total_tokens=user.get("tokens")
        
        total_messages = 0
        for chat_id in chat_ids:
            # Fetch chat details from the chats collection
            chat = st.session_state.mongo.chat_history.find_one({"_id": chat_id})
            if chat:
                messages = chat.get("messages")  # Sum of the number of messages in each chat
                total_messages+=len(messages)
        
        # Add this user’s data to the list
        user_data.append({
            "User ID": user_id,
            "Email": email,
            "Chat Sessions": len(chat_ids),
            "Total Messages": total_messages/2,
            "Tokens_consumed":total_tokens
        })
    
    # Convert the list of user data to a DataFrame for better table display in Streamlit
    return pd.DataFrame(user_data)

# Streamlit App to display the admin dashboard
def show_admin_dashboard(logout_callback):
    st.title("Admin Dashboard")
    st.write("Welcome, Admin!")
    
    # Fetch and display user data
    user_data_df = get_user_data()
    
    if user_data_df.empty:
        st.write("No data available.")
    else:
        st.subheader("User Data ")
        st.dataframe(user_data_df)  
    if st.button("Logout"):
        logout_callback()    




   