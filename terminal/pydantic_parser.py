from typing import List
from config import load_google_llm
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate

llm=load_google_llm()

print("loading pleasewait......")

# Force LLM TO GIVE OUTPUT IN A SPECIFIC FORMAT

class Recipe(BaseModel):
    name: str
    ingredients: List[str]  
    instructions: str
    prep_time: int = Field(..., description="Preparation time in minutes")
    cook_time: int = Field(..., description="Cooking time in minutes")
    servings: int   

    # DONE WITH OUR TYPES
parser = PydanticOutputParser(pydantic_object=Recipe)

prompt_template=PromptTemplate.from_template(
    """Based on the food provided {food}, provide a recipe, together with other information in the following JSON format :
    {{ 
     "name":string,
     "ingredients":list[string],
     "instructions":string,
     "prep_time":int,
    "cook_time":int,
     "servings":int
    }}
    """)
user_food=input("Please enter the food you have\n")
prompt=prompt_template.format(
    food=user_food
)

response=llm.invoke(prompt)
print(f"response is: {response}")
try:
    parsed_result=parser.parse(response)
    print("THE PARSED RESULT IS: ",parsed_result)
    print(f"THE PARSED RESULT Name is:  ",parsed_result.name)
except Exception as e:
    print("Parsing failed! Raw response:", response)
    print("Error details:", e)