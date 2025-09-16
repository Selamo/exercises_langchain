# from config import load_google_llm
# llm=load_google_llm()
# print(f"My llm model is: {llm}")

# response=llm.invoke("Who is the Goat of football in less than 1 word")
# print(f"My response is: {response}")
# prompt = Programming language for LLMs

from config import load_google_chat_model
llm=load_google_chat_model
prompt= input("Hello\n")
response=llm.invoke(prompt)
print(f"My response is: {response}")
