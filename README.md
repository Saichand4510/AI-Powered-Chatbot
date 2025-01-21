# AI Powered Chatbot

**Overview**<br>

This project provides a platform where users can:

- Sign up and log in to access personalized sessions.

- Interact with a chatbot interface.

- Create multiple chatbot sessions for different conversations.

- Admins can log in to access the admin dashboard and monitor user activity.

- Chat history is saved and can be revisited.

The application is built using Python 3.10, with the interface powered by Streamlit.

# Prerequisites

**Python Version:** Ensure Python 3.10 is installed on your system.

**Conda:** Install Anaconda .

### Setup Instructions

***1. Clone the Repository***

```bash
$ git clone <repository_url>
```
```bash
$ cd <repository_directory>
```

***2. Create a Conda Environment***
```
$ conda create -n chatbot_env python=3.10 -y
```
```
$ conda activate chatbot_env
```
***3. Install Required Packages***

- Use the requirements.txt file to install all necessary dependencies.

```
$ pip install -r requirements.txt
```
***4.API KEYS and MongoDb string***
- Replace the API KEYS and MongoDB connection string with your in .env file

***5. Run the Application***

- Start the Streamlit application.

```
$ streamlit run app.py
```

# Usage Instructions

***1. Sign Up / Log In***

**Sign Up:** New users must register by providing basic details (e.g., username and password).

**Log In:** Existing users can log in to access their dashboard.

***2. User Interface***

**After logging in:**

- You will see the chatbot interface.

- You can create multiple sessions to manage different conversations.

***3. Chat with the Bot***

- Type your messages in the input field.

- View responses in the chat window.

- Chat history is saved automatically and can be revisited.

***4. Manage Sessions***

- Use the ****"Create New Session"**** option to start a new conversation.

- Previous sessions can be revisited and continued.

***5. Admin Dashboard***

- On the first page, click the Admin Login option.

- Log in with admin credentials username:admin password:admin123 to access the admin dashboard.

- The admin dashboard provides insights into user activity, including:<br>
    - Chatbot usage statistics. 
