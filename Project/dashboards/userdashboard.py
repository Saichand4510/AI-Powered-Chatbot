import os   
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.indices.postprocessor import SimilarityPostprocessor
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
import streamlit as st
from llama_index.core.llms import ChatMessage
from llama_index.llms.groq import Groq
import tiktoken
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from pathlib import Path
from dotenv import load_dotenv
script_path = Path(__file__).resolve()
main_folder_path = script_path.parent.parent 
env_path = os.path.join(main_folder_path, '.env')
load_dotenv(dotenv_path=env_path) 

def initialize():
    ###### code for model selection   
            api_key = os.environ["PINECONE_API_KEY"]
            embed_model = OpenAIEmbedding(model="text-embedding-3-small")
            menu = ["gpt-4o"]
            choice = st.sidebar.selectbox("Models", menu)
            llm=OpenAI(model="gpt-4o",temperature=0.5)
            if choice == "gpt-4o":
                llm=OpenAI(model="gpt-4o",temperature=0.5)
           # elif choice == "llama-3.3":
            #    llm = Groq(model="llama-3.3-70b-versatile")
            
              
            with st.sidebar:
                st.title("Chat Sessions")
    
    ########### Session management
                st.subheader("All Sessions")
          
                st.session_state.chat_sessions=st.session_state.mongo.get_chat_sessions(st.session_state.username)
            
                st.session_state.chat_session_names=st.session_state.mongo.get_chat_session_names(st.session_state.username)
          
                i=0
                for session_name in st.session_state.chat_sessions:
                         
                         if st.button(st.session_state.chat_session_names[i]):  # Create a button for each session
                               st.session_state.current_session = session_name
                               st.session_state.messages=st.session_state.mongo.get_chat_messages(session_name) # get messages for the session where button clicked
                             
                               del st.session_state['memory'] 
                         i=i+1

    ######### Create New Chat Session
                st.subheader("Create New Session")
                new_session_name = st.text_input("Session Name:", placeholder="Enter new session name...")
                if st.button("Create Session"):
                        if new_session_name.strip() and new_session_name not in st.session_state.chat_session_names:
                                
                                id=st.session_state.mongo.create_new_chat_session(st.session_state.username,new_session_name)
                                st.session_state.chat_sessions.append(id) 
                                
                                st.session_state.current_session = id
                                st.session_state.messages=st.session_state.mongo.get_chat_messages(id)
                                st.success(f"Session '{new_session_name}' created!")
                                del st.session_state['memory']
                                st.rerun()
                        elif new_session_name.strip() in st.session_state.chat_session_names:
                                st.warning("Session name already exists!")
                        else:
                                st.error("Please enter a valid session name!") 
                if  "current_session" not in st.session_state : 
                     st.session_state.current_session = st.session_state.chat_sessions[0]
                     st.session_state.messages=st.session_state.mongo.get_chat_messages(st.session_state.current_session)
            Settings.embed_model = embed_model
            Settings.llm=llm
    ##### Initializing pinecone and creating query engines for all indexes and created query engine tool
            pc = Pinecone(api_key=api_key)
            indexa=pc.Index("apolloreports")
            vector_storea = PineconeVectorStore(pinecone_index=indexa)
            indexs=pc.Index("sbicardreports")
            vector_stores = PineconeVectorStore(pinecone_index=indexs)
            indexz=pc.Index("zomatoreports")
            vector_storez = PineconeVectorStore(pinecone_index=indexz)
            vector_indexa = VectorStoreIndex.from_vector_store(vector_store=vector_storea)
            retrievera=VectorIndexRetriever(index=vector_indexa,similarity_top_k=10)
            postprocessor=SimilarityPostprocessor(similarity_cutoff=0.4)
            apollo_engine=RetrieverQueryEngine(retriever=retrievera,
                                  node_postprocessors=[postprocessor])
            vector_indexs = VectorStoreIndex.from_vector_store(vector_store=vector_stores)
            retriever=VectorIndexRetriever(index=vector_indexs,similarity_top_k=10)
            sbicard_engine=RetrieverQueryEngine(retriever=retriever,
                                  node_postprocessors=[postprocessor])
            vector_indexz = VectorStoreIndex.from_vector_store(vector_store=vector_storez)
            retrieverz=VectorIndexRetriever(index=vector_indexz,similarity_top_k=4)
           
            zomato_engine=RetrieverQueryEngine(retriever=retrieverz,
                                  node_postprocessors=[postprocessor])
            query_engine_tools = [
    QueryEngineTool(
        query_engine=apollo_engine,
        metadata=ToolMetadata(
            name="apollo",
            description=(
                "Provides information about apollo  for year 2020,2021,2022,2023. "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=sbicard_engine,
        metadata=ToolMetadata(
            name="sbicard",
            description=(
                "Provides information about annual reports of sbicard for year 2020,2021,2022,2023 "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=zomato_engine,
        metadata=ToolMetadata(
            name="zomato",
            description=(
                "Provides information about annual reports of zomato for year 2020,2021,2022,2023 "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
]
            context = """
You are  expert in Q&A on the companies apollo,sbicard,zomato.
   You will answer questions about the annual reports of zomato,sbicard,apollo . don't answer queries  which are irrelevant of the provided  
"""
            return query_engine_tools,context,llm

def render_user_dashboard(username, logout_callback):
    query_engine_tools,context,llm= initialize()
    token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model(llm.model).encode)
    

# Creating a CallbackManager with the token counter
    callback_manager = CallbackManager([token_counter])
    st.write(f"Welcome, {username}!")
    st.subheader("Chat with Financial Chatbot")
    k=0
    for i in st.session_state.chat_sessions:
         k=k+1
         if i==st.session_state.current_session:
              break     
    st.subheader(f"Using session :{st.session_state.chat_session_names[k-1]}")
    if "memory" not in st.session_state:
       st.session_state.memory= ChatMemoryBuffer.from_defaults(token_limit=2000)
       if st.session_state.messages:
         for message in st.session_state.messages:
           #print("memory is good")
           st.session_state.memory.put(ChatMessage(role=message['role'], content=message['content']))
    
    ###### creating functional agent with the query_engine tools       
    agent_worker = FunctionCallingAgentWorker.from_tools(
    query_engine_tools,
    llm=llm,
    callback_manager=callback_manager,
    verbose=True,
    system_prompt=context,
    )
    ####### making agent has context of coversational history
    agent = AgentRunner(agent_worker,memory=st.session_state.memory)
    st.markdown(
        """<style>
            .chat-bubble {
                border-radius: 15px;
                padding: 10px;
                margin: 5px 0;
                max-width: 100%;l
            }
            .human {
                background-color: #000000;
                align-self: flex-end;
            }
            .ai {
                background-color: #000000;
                align-self: flex-start;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
             .input-section {
            position: fixed;
            bottom: 0;
            width: 100%;
          
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    ######## Chat Interface
    chat_container = st.container()
    with st.form(key="chat_form"):
    ######## Text input field inside the form
        st.markdown("<div class='input-section'>", unsafe_allow_html=True)
        query = st.text_input("Ask a question:", placeholder=f"Type your question here...using session:{st.session_state.chat_session_names[k-1]}")

    ######### Submit button for the form
        submit_button = st.form_submit_button(label="Submit") 
    e=""
    if query and submit_button:
             message = agent.chat(query+" use only tools")
          ##########push query and answer in mongodb
             e=message.response
             l={"role":"user","content":query}
             s={"role":"assistant","content":e}
             st.session_state.messages.append(l)
             st.session_state.messages.append(s)

    ##########3 Display Chat History
    with chat_container:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        l=st.session_state.messages
        if l:
         for i in l:
            if i['role']=='user':
                st.markdown(f"<div class='chat-bubble human'><bold>USER:</bold>{i['content']}</div>", unsafe_allow_html=True)
            elif i['role']=='assistant':
                st.markdown(f"<div class='chat-bubble ai'><bold>AI:</bold>{i['content']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    ######### Scroll Behavior 
    st.markdown(
        """<script>
            var container = window.parent.document.querySelector('.stApp');
            container.scrollTop = container.scrollHeight;
        </script>
        """,
        unsafe_allow_html=True
    )
    if st.sidebar.button("Logout"):
        del st.session_state['memory']
        st.session_state.chat_sessions=[]
        st.session_state.chat_session_names=[]
        
        
        del st.session_state['current_session']
        logout_callback()  
        
    if query and e:
        total_tokens = token_counter.total_llm_token_count
        return query,e,total_tokens
    return ("","",0)  





