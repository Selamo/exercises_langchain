from langchain_core.prompts import ChatPromptTemplate
from config import load_google_chat_model
chat_model=load_google_chat_model()

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "you are an {expert} in {domain}, please break down any question the user is going to ask you in a clear and a coincise manner with a real world analogy"),
    ("user", "Please {expert} help me with my question"),
    ("ai", "Sure, {name}, I can do just that"),
    ("user", "{user_input}")

])

prompt=chat_prompt.format_messages(
    expert="Gen Ai Engineer",
    domain="Artificial Intelligence",
    name="Allino",
    user_input="Please explain Transformers in GenAi to me, as if I was 6 years, but should not be more than 300 words"
)
print("Loading Please wait......")
response=chat_model.invoke(prompt)
print(f"response is: {response.content}")
for part in chat_model.stream(prompt):
    print(part.content, end="", flush=True)
