# We want to connect our env from the .env file
import os
import datetime
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import GoogleGenerativeAI

load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Connecting LLMS
Llm = GoogleGenerativeAI(temperature=0.7, model="gemini-2.5-pro", api_key=GOOGLE_API_KEY)
# res =Llm.invoke("Write a poem about AI in the style of Shakespeare")

# Write a Simple Function called Daaily Journal
# mood and the event: so ai now givve you a reflection and what you need to improve

def daily_journal():
    print("Welcome to my Daily Journal App!")
    print("_"*50)

    # Get inpt from the user
    mood = input("What Happened Today?\n")
    event= input("How was your mood today?\n")

    prompt = f"Help me reflect on my day Today {mood}. i felt {event}. Give me a reflection and what i need to improve tommorow"

    print("REFLECTION FROM AI")
    print("_"*50)
    for part in Llm.stream(prompt):
        print(part, end="", flush=True)
    with open("journal.txt", "a") as f:
        f.write("datetime.now()\n")
        f.write(f"Today I felt {event} because {mood}\n")
        f.write(f"AI Reflection: {part}\n")
        f.write("_"*50 + "\n")
        for part in Llm.stream(prompt):
            f.write(part)
        f.write("\n"+"_"*50 + "\n")

#Call our function
daily_journal()