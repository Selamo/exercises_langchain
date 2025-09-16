from config import load_google_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# One runnable
# Why it recive a prompt and send out output

llm=load_google_llm()

chat_template=ChatPromptTemplate.from_messages([
    ('system', "You are a football analyst, your work is to answer users {question} and straight forward answer"),
    ('user', 'Tell me more about {player} playing for {club}')
])

player_input=input("Enter your favorite player:")
question_input=input(f"What do you want to know about: {player_input}?")
club_input=input(f"Enter {player_input} club: ")

parser=StrOutputParser()

chain=chat_template | llm | parser

output=chain.invoke({
    "question":question_input,
    "player":player_input,
    "club":club_input
})

print(f"output is: {output}")