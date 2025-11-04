from fastapi import FastAPI, UploadFile, File, HTTPException
import base64
from config import load_google_chat_model
llm=load_google_chat_model()

app=FastAPI()
@app.post("/process-image")
async def process_image(file:UploadFile=File(...)):
    try:
        # get image and convert it to byte
        image_bytes = await file.read()
        # cpu is going to be idle
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        format_image=f"data:image/jpeg;base64,{image_base64}"
        # pass image to llm to decode
        prompt=f"""
        Given the image : {format_image}, please analyze, doing step by step and let us know what is inside this image"""

        response=llm.invoke(prompt)
        return {
            "response":response.content,
            "file":file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occured")