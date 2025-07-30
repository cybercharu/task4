from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from .auth import hash_password,authenticate_user, create_access_token
from datetime import timedelta
from bson import ObjectId
from .model import RegisterUser,Token
from .database import db, collection
from dotenv import load_dotenv
import os

load_dotenv()  
ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()

@app.get("/hello/{name}")
def hello(name):
    return f"welcome to RESTful API for a movie library application,{name}"

@app.post("/register")
def register_user(data: RegisterUser):
    existing_user = collection.find_one({"cust_email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(data.password)

    user_data = {
        "cust_id": str(ObjectId()),
        "cust_email": data.email,
        "cust_name": data.username,
        "password": hashed_pw,
        "role": data.role
    }

    collection.insert_one(user_data)

    return {
        "message": "User created successfully",
        "users": {
            "email": user_data["cust_email"],
            "name": user_data["cust_name"],
            "role": user_data["role"]
        }
    }

@app.post("/token",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
    data={"sub": form_data.username, "role": "consumer"},
    expires_delta=access_token_expires
)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

