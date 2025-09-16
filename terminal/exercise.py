from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
from config import load_google_chat_model
chat_model=load_google_chat_model()

loader=PyPDFLoader('./data/ai.pdf')
text_loader=TextLoader('./data/ai.txt')
final_text=text_loader.load()
# print("My loaded text data is: ",final_text)
load_data=loader.load()

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a personal assistant, you are to help the user answer questions based "
    "on {final_text} provided to you, anything outside it, politely say you don't know"),
    ("user", "{user_input}")
])
user_input=input("Please enter your question: \n")
prompt=chat_prompt.format_messages(
    final_text=final_text,
    user_input=user_input

)
while True:
    # user_input=input("User😎: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chat ended. Goodbye!..........")
        break
    print("Loading Please wait......")
    response=chat_model.invoke(prompt)
    for part in chat_model.stream(user_input):
        print(part.content, end="", flush=True)