from llama_parse import LlamaParse
import os
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from pinecone import Pinecone, ServerlessSpec

from llama_index.vector_stores.pinecone import PineconeVectorStore
from dotenv import load_dotenv
load_dotenv()
api_key =os.environ['PINECONE_API_KEY'] 
llama_api_key=os.environ['LLAMA_API_KEY']   

pc = Pinecone(api_key=api_key)

embed_model = OpenAIEmbedding(model="text-embedding-3-small")

Settings.embed_model = embed_model

loader = LlamaParse(api_key=llama_api_key,result_type="markdown",gpt4o_mode=True,gpt4o_api_key=os.environ['OPENAI_API_KEY'])
p="C:/Users/SaiChandLinga(Quadra/Desktop/Capstone_Project/financial_reports/apollo"#similary for other folders  

l=os.listdir("C:/Users/SaiChandLinga(Quadra/Desktop/Capstone_Project/financial_reports/apollo")
print(l)
splitter = SentenceSplitter()
pc.create_index(
        name="apolloreports",
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 
print("Created Index")
index=pc.Index("apolloreports")
vector_store = PineconeVectorStore(pinecone_index=index)
print("vector store created")
def parser(path):
       file_path=p+"/"+path 
       documents = loader.load_data(file_path=file_path) 
       print("loaded file of "+path) 
       nodes = splitter.get_nodes_from_documents(documents)
       print("Splitted documents for "+path)
       k=0
       for node in nodes:
         if node.text!="":
           node_embedding = embed_model.get_text_embedding(node.text)
           node.embedding = node_embedding
           k=k+1
       print(k)
       print("Converted to embeddings for "+path)    
       l=[]
       for i in nodes:
         if i.embedding!=None:
          l.append(i)    
       vector_store.add(l)  
       print("Stored embeddings for "+path+" in db")  



for i in l:
   parser(i) 

 
        
 


        



    