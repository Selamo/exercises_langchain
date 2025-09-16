from config import load_google_llm
#  import the output
from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain_core.prompts import PromptTemplate

# parser=StrOutputParser()
parser=JsonOutputParser()
llm=load_google_llm()

# prompt_template=PromptTemplate.from_template(
#     """"Tell me a joke about {topic} in less than 20 words"""
# )

# user_topic=input("Please enter the topic\n")
# prompt=prompt_template.format(
#     topic=user_topic
# )
# response=llm.invoke(prompt)
# formated_output=parser.parse(response)
# print("loading pleasewait......")
# print(f"formated output is: {formated_output}")
#llm
# print(f"response is: {response}")
# for part in llm.stream(prompt):
#     print(part, end="", flush=True)


prompt_template=PromptTemplate.from_template("""
Please you are now acting as a professional football analyst, for a given football player{player}, provide info in the following JSON format:

{{

"name":string,
"age":int,
"position":string,
"team":string,
"nationality":string,
"appearances":int,
"goals":int,
"assists":int,
"trophies":list[string]
}}

the image url should be fetched from pintress like pixels 
"""
)
user_player=input("Please enter your favorite football player\n")
prompt=prompt_template.format(
    player=user_player
)
print("loading pleasewait......")
response=llm.invoke(prompt)
formated_output=parser.parse(response)
print(f"formated output is: {formated_output}")

