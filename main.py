from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

@app.get("/")
def get_doc():
    return {
        "message": "Hello world"
    }
