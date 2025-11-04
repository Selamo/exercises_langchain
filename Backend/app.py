from fastapi import FastAPI, Body
from typing import Optional
from pydantic import BaseModel
# initialize fastapi class
app=FastAPI()

# Start using it to create a server
# @app.get("/hello")
# def hello_deepseeds():
#     return{
#         "data":"hello deepseeds"
#     }

# @app.get("/sentiment-analysis")
# def analyzing_sentiments():
#     # after logic here
#     # after then return the data
#     return{
#         "sentiment_score":"score-0.7",
#         "platform":"huggingface",
#         "sentiment":"Positive",
#         "model":"distilbert-id"
#     }

# # Create an point : that returns information about you(name, email, favMeal, age)
# @app.get("/Myself")
# def myself():

#     return{
#         "name": "Selamo Allen Leinyuy",
#         "email": "selamo@gmail.com",
#         "favMeal": "fufu",
#         "age": "15"
#     }
# # TOPIC2 : PATH PARAMETERS

# @app.get("/sentiment/{text}")
# def analyze_sentiment(text):
#     if text.lower() in ["good", "nice", "great"]:
#         return {
#             "sentiment":"positive",
#             "score":"sentiment-score",
#             "model":"bert-345"
#         }
#     return {
#         "sentiment":"negative",
#         "score":"negative score",
#         "model":"model"
#     }

    #Exercise: 
    # 1. Take a pprompt from the user, pass it as a path parameter to your endpoint
    # 2. Also pass it to your llm to get response
    # 3. return: {"user_prompt":prompt, "ai_response":response}

from config import load_google_llm
@app.get("/prompting/{prompt}")
def user_prompt(prompt):
    llm=load_google_llm()
    # prompt=input("Enter the prompt")
    response=llm.invoke(prompt)
    return{
        "user_prompt":prompt,
        "ai_response":response
    }



# # Another
# @app.get("/get-config/{temperature}")
# def get_config(temperature:float):
#     if temperature <0 or temperature >1:
#         print("temperature can never be less than 0 or more than 1")
#         return {
#             "error":"temperature should be between 0 and 1"
#         }
#     return{
#         "temperature":temperature
#     }

# @app.get("/config/{top_p}")
# def get_config(top_p):
#     return {
#         "data":""
#     }

# dictionary of data
data={
    1:{
        "name":"product 1",
        "price":"150XAF",
        "date_posted":"12-6-2025"
    },
    2:{
        "name":"product 2",
        "price":"2000XAF",
        "date_posted":"12-7-2025"
    },
    3:{
        "name":"product 3",
        "price":"3000XAF",
        "date_posted":"12-8-2025"
    }
}

# @app.get("/search")
# def search(id:int):
#     if id in data:
#         return{
#             data[id]
#         }
#     return {
#         "error":"not available"
#     }


#QUERY PARAMETERS
@app.get("/search-product")
def search_product(category:str, page:int, id:Optional[int]=None):
    if id in data:
        filterdData=data[id]
    else:
        return{
            "error":"Sorry not found"
        }
    return{
        "data":filterdData
    }
    #Pass the category, page and id, in the url endpoint and test

# REQUEST BODY
class UserData(BaseModel):
    name:str
    age:int
    favMeal:str
    isMarried:bool

@app.post("/posting-data")
def posting_data(request:UserData):
    # expecting data from the client
    return {
        # "data":"my data back",
        "data":request
    }

class AiData(BaseModel):
    model_name:str
    model_id:int
    prompt:str

@app.post("/ai-data")
def ai_data(request:AiData):
    return{
        "data":request
    }


from fastapi import FastAPI, UploadFile, File, HTTPException
import base64
from config import load_google_chat_model
llm=load_google_chat_model()


@app.post("/process-image")
async def process_image(file:UploadFile=File(...)):
    try:
        # get image and convert it to byte
        image_bytes = await file.read()
        # cpu is going to be idle
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        format_image=f"data:image;base64,{image_base64}"
        # pass image to llm to decode
        prompt=f"""
        Given the image : {format_image}, please analyze, doing step by step and let us know what is inside this image"""

        response=llm.invoke(prompt)
        return {
            # "image_bytes":image_bytes,ki
            # "image_b64":image_base64,
            "response":response.content,
            "file":file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured")