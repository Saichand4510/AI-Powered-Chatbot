from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the absolute path of the current script



class MongoDb():
      
        def __init__(self):
           script_path = Path(__file__).resolve()


           main_folder_path = script_path.parent.parent 
        
        
           env_path = os.path.join(main_folder_path, '.env')
           
           load_dotenv(dotenv_path=env_path)        
           mongo_url = os.environ["MONGO_DB_URL"]
           self.client = MongoClient(mongo_url)
           self.db = self.client["chat_app"]
           self.users= self.db["users"]
           self.chat_history=self.db["chat_history"]
           #print("1")
           try:
               self.client.admin.command('ping')
               print("Pinged your deployment. You successfully connected to MongoDB!")
           except Exception as e:
                print(e)

        def create_new_user(self,user_name,gmail):
             new_user={
                  "_id":user_name,
                  "gmail":gmail,
                  "chat_history":[],
                  "chat_names":[],
                   "tokens":0
                }
             self.users.insert_one(new_user)
             
        def create_new_chat_session(self,user_id,chat_name):
           # Create a new chat session for a user
          

            new_session = {
                  
                       "user_id": user_id,
                        "messages":[]
                            }
              
            result=self.chat_history.insert_one(new_session)
            self.users.update_one(
                 {"_id":user_id},
                 {
                     "$push":{"chat_history":result.inserted_id,"chat_names": chat_name  } 
                     
                      
                 }
               

            )
            
            return result.inserted_id

        def add_message_to_chat_session(self, session_id, role, content):
    # Add a message to an existing chat session.
            message = {"role": role, "content": content}
            self.chat_history.update_one(
            {"_id": session_id},
        {
            "$push": {"messages": message}  # Fix the syntax error and push to the "messages" field.
        }
    )

        def get_chat_sessions(self,user_id):
#Retrieve current chat sessions.
            user_chat_sessions= self.users.find_one({"_id": user_id})
            return user_chat_sessions["chat_history"] if user_chat_sessions else []
        def get_chat_session_names(self,user_id):
             user_chat_session_names=self.users.find_one({"_id":user_id})
             return user_chat_session_names["chat_names"] if user_chat_session_names else []
        def get_chat_messages(self, session_id):
#Retrieve all messages from a specific chat session.
             
              user_data = self.chat_history.find_one(
                   {"_id": session_id},
                   
               )
              if user_data:
                  return user_data["messages"]
              return []
        def add_tokens(self,user_id,tokens):
             user_tokens= self.users.find_one({"_id": user_id})
             updated_tokens = user_tokens.get("tokens") + tokens
             self.users.update_one(
                   {"_id": user_id},
                  {"$set": {"tokens": updated_tokens}}
                  )
        def get_tokens(self,user_id):
             user_tokens=self.users.find_one({"_id":user_id})
             tokens_consumed=user_tokens.get("tokens")
             return tokens_consumed     
      


   
