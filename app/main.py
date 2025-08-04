from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from .auth import hash_password,get_current_user, create_access_token
from datetime import timedelta
from bson import ObjectId
from .model import RegisterUser,Token
from .database import collection, movie_collection
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
    data={"sub": form_data.username, "role": "user"},
    expires_delta=access_token_expires
)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/movies/")
def create_movie( movie_id: int, moviename: str,   moviedesc: str, moviegenre: str,movieyear: int,get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create movies")
    else:
        movie_data = {
            "movie_id": movie_id,
            "moviename": moviename,
            "moviedesc": moviedesc,
            "moviegenre": moviegenre,
            "movieyear": movieyear,
            "created_by": get_current_user["username"]
        }
        movie_collection.insert_one(movie_data)
        return movie_data

@app.put("/movies/{movie_id}")
def update_movies(movie_id: int, moviename: str, moviedesc: str, moviegenre: str, movieyear: int, get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update movies")

    result = movie_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {
            "moviename": moviename,
            "moviedesc": moviedesc,
            "moviegenre": moviegenre,
            "movieyear": movieyear,
            "updated_by": get_current_user["username"]
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found or no change")

    return {"message": "Movie updated successfully"}


@app.delete("/movies/{movie_id}")
def delete_movies( movie_id: int, get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create movies")
    result = movie_collection.delete_one({"movie_id": movie_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"message": f"Movie {movie_id} deleted successfully"}

@app.get("/movies")
def get_all_movies():
    movies_cursor = movie_collection.find({}, {"_id": 0})  
    movies = list(movies_cursor)  
    return movies

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = movie_collection.find_one({"movie_id": movie_id}, {"_id": 0})  

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


