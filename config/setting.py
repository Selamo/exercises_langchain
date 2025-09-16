import requests
import os
from pprint import pprint
# from langchain_google_genai.embeddings.
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
def environmental_variables():
    import os
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # print("My Api keys loading...")
    # print(GOOGLE_API_KEY, OPENAI_API_KEY, GROQ_API_KEY)

# load google llm
def load_google_llm():
    from langchain_google_genai import GoogleGenerativeAI
    #loading our keys
    environmental_variables()
    google_llm=GoogleGenerativeAI(
        # pass our configurations here
        model="gemini-2.5-flash",
        temperature=0.9,
    )
    return google_llm

def load_google_chat_model():
    from langchain_google_genai import ChatGoogleGenerativeAI
    environmental_variables()
    google_chat_model=ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.9,
    )
    return google_chat_model

# Configure weather API end point
class WeatherAPILoader:
    # Create a Constructor function
    def __init__(self, city, api_key):
        # initialize properties
        self.city=city
        self.api_key=api_key
        # Create A method that loads the data
    def load(self):
            # we need to pass some information to our url like the city and api_key
        url=f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
        response=requests.get(url).json()
        return response

# initialize the class or an instance
def weatherContext(city):
    import os
    environmental_variables()
    weatherData=WeatherAPILoader(city=city, api_key=os.getenv("WEATHER_API_KEY"))

    response=weatherData.load()
    return response


def load_embeddings():
    environmental_variables()
    embeddings= GoogleGenerativeAIEmbeddings(
        model= "models/text-embedding-004",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    print("embeddings", embeddings)
    # Test with sample text
    # Embeddings work by converting text to numerical representations(vectors) that cap
    #that meaning

    sample_text= [
        "The day is a bright day",
        "I love music",
        "I support my country",
        "Machine learning is fascinating"
    ]
    print("Generating embeddings for the sample text...")
    print("_"*50)

    # Generate embeddings for multiple texts at once
    # This is more efficient than generating them one by one

    embedded_docs= embeddings.embed_documents(sample_text)
    # print(embedded_docs)
    return embeddings

# load_embeddings()






class NewsAPILoader:
    # Create a Constructor function
    def __init__(self,query, api_key):
        # initialize properties
        # self.city=city
        self.api_key=api_key
        self.query=query
        # Create A method that loads the data
    def load(self):
            # we need to pass some information to our url like the city and api_key
        # url=f"https://newsdata.io/api/1/news?q={}apikey={self.api_key}&country={self.country} &language=en"
        url=f"https://newsdata.io/api/1/latest?q={self.query}&apikey={self.api_key}"
        response=requests.get(url).json()
        return response

# initialize the class or an instance
def newsContext(query):
    from pprint import pprint
    import os
    environmental_variables()
    weatherData=NewsAPILoader(query=query,api_key=os.getenv("NEWS_API_KEY"))
    # print(os.getenv("NEWS_API_KEY"))
    response=weatherData.load()
    # pprint(response)
    return response
# newsContext()

