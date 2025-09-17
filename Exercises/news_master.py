# - Use your existing  # PromptTemplate pattern - Create prompts that take news article and # generate: - AI summary (2 sentences max) - Sentiment analysis (positive/ # negative/neutral) - Key topics extraction (3-5 topics) - Credibility assessment  
from config import load_google_llm, newsContext 
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import PydanticOutputParser 
from pydantic import BaseModel, Field 
from langchain_core.prompts import PromptTemplate 
from pprint import pprint  

import firebase_admin 
import os 
from firebase_admin import credentials, firestore  

script_dir = os.path.dirname(file) 
key_path = os.path.join(script_dir, "serviceAccountKey.json") 
cred = credentials.Certificate(key_path) 
firebase_admin.initialize_app(cred)  

db = firestore.client() 
print("Firebase connected ✅")   

llm=load_google_llm()   

class News(BaseModel):     
    title: str     
    article: str     
    ai_summary: str     
    sentiment_analysis: str     
    key_topics: str     
    credibility_assesment: str     
    pidgin_version: str  

parser = PydanticOutputParser(pydantic_object=News)  

query=input("Which city are you interested in news for? ") 
my_tool=newsContext(query)   

prompt_template=PromptTemplate.from_template( 
    """You are a news master that recieve news articles: {context}, generate a summary in 2 sentences max, and a pidgin verision together with the other information in the following JSON format :  
    {{    
    "title:string,   
    "article:string,   
    "ai_summary:string,   
    "sentiment_analysis:string,   
    "key_topics":string,   
    "credibility_assesment":string   
    pidgin_version:string  
    }}     
    """ 
) 

query=input("Please enter the country\n") 
prompt=prompt_template.format(     
    context=my_tool 
)   

response=llm.invoke(prompt) 
print(f"response is: {response}") 

try:     
    parsed_result=parser.parse(response)     
    print("THE PARSED RESULT IS: ",parsed_result)     
    print(f"THE PARSED RESULT Name is:  ",parsed_result.title)     
    try:         
        # Convert the Pydantic model to a dictionary         
        news_data = parsed_result.dict()                  
        # Add the data to Firestore         
        doc_ref = db.collection("news_articles").add(news_data)         
        print(f"Successfully stored news article with ID: {doc_ref[1].id}")      
    except Exception as e:         
        print(f"Error storing data in Firestore: {e}") 
except Exception as e:     
    print("Parsing failed! Raw response:", response)     
    print("Error details:", e)  
