# TEMPLATE

# WHAT IS A PROMPT TEMPLATE?
# propt template is inputing variables in your prompt
from langchain_core.prompts import PromptTemplate

from config import load_google_llm
llm=load_google_llm()

prompt_template=PromptTemplate.from_template(
    # "Please base on the topic: {topic}, explain the concept to the user as if he/she was 12"
    "Given book title {title} and the {author} write a a clear and clean summary"
)
# Where should we accept this input

print("WELCOME TO MY LEARNING APP")
print("_"*70)

# recieve info from the user
user_title=input("PLease enter your favorite book title:\n")
user_author=input("Please enter the author of the book:\n")

prompt=prompt_template.format(
    title=user_title,
    author=user_author
)
# print output to the user
print("loading......")
response=llm.invoke(prompt)
print(f"response is: {response}")
for part in llm.stream(prompt):
    print(part, end="", flush=True)