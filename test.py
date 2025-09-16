# We want to connect our env from the .env file
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import GoogleGenerativeAI

# load_dotenv(find_dotenv())
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # Connecting LLMS
# Llm = GoogleGenerativeAI(temperature=0.7, model="gemini-2.5-pro", api_key=GOOGLE_API_KEY)
# res =Llm.invoke("Write a poem about AI in the style of Shakespeare")
# # print(f"Response fromAI is: {res}")

# # Streaming.........
# # In streaming when the ai start generating t start displaying in the screen

# for part in Llm.stream("Pleaase explain with statistics who is better, Messi or Ronaldo?"):
#     print(part, end="", flush=True)
