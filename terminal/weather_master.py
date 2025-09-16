from config import load_google_llm, weatherContext
from langchain_core.prompts import ChatPromptTemplate
llm=load_google_llm()

city=input("Where are you currently")
my_tool=weatherContext(city)

messages=[
    ("system", "You are a weather master that answer user questions based on: {context}, i want you to advice users on what to wear, what to do and how to prepare the day"
    "Be flexible and always answer user queries and it should never go off topic")
]
chat_template=ChatPromptTemplate.from_messages(messages)
while True:
    user_input=input("USER: ")
    if user_input.lower() in ["quite","exit"]:
        print("Exiting")
        break
    messages.append(("human",user_input))
    prompt=chat_template.format_messages(
        context=my_tool
    )
    response=llm.invoke(prompt)
    # messages.append("ai", response)
    print(response)