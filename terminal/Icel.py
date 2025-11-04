from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import load_google_llm

prompt = PromptTemplate(
    input_variables=['product_description'],
    template="Give a Brand name for the following tech startup: {product_description}"
)
llm=load_google_llm()

chain=LLMChain(llm=llm, prompt=prompt)
result=chain.invoke(product_description="A software developmrnt tech starrtup")
print(f"Results are : {result}")