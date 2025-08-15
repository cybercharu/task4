from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import OAuth2PasswordRequestForm
from .auth import hash_password,get_current_user, create_access_token
from datetime import timedelta,datetime
from bson import ObjectId
from .model import RegisterUser,Token,Movies
from .database import collection, movie_collection,rental_collection
from dotenv import load_dotenv
import os

load_dotenv()  
ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

app = FastAPI()

@app.get("/")
def index():
    return{"hello world"}

# welcoming user to my API page
@app.get("/hello/{name}")
def hello(name):
    return f"welcome to RESTful API for a movie library application,{name}"

# Allow users to register themselves
@app.post("/register")
def register_user(data: RegisterUser):
    existing_user = collection.find_one({"cust_email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(data.password)

    user_data = {
        "cust_id": str(ObjectId()),
        "cust_email": data.email,
        "username": data.username,
        "password": hashed_pw,
        "role": data.role
    }

    collection.insert_one(user_data)

    return {
        "message": "User created successfully",
        "users": {
            "email": user_data["cust_email"],
            "name": user_data["username"],
            "role": user_data["role"]
        }
    }
# Allow users to login with their username and password
@app.post("/token",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
    data={"username": form_data.username, "role": "role"},
    expires_delta=access_token_expires
)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# allow user (admin) to create movies
@app.post("/movies/")
def create_movie(moviename: str, moviedesc: str, moviegenre: str, movieyear: int,available:bool,get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create movies")
    last_movie = movie_collection.find_one(sort=[("movie_id", -1)])
    if last_movie and "movie_id" in last_movie:
        new_movie_id = last_movie["movie_id"] + 1
    else:
        new_movie_id = 1

    movie = {
        "movie_id": new_movie_id,
        "moviename": moviename,
        "moviedesc": moviedesc,
        "moviegenre": moviegenre,
        "movieyear": movieyear,
        "available": True,
        "created_by": get_current_user["username"]
    }
    result = movie_collection.insert_one(movie)
    return {"message": "Movie created", "movie_id": new_movie_id, "movie_org_id": str(result.inserted_id)}

# allow user(admin) to update movies
@app.put("/movies/{movie_id}")
def update_movies(movie_id: int,movie_data: Movies,get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update movies")

    result = movie_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {
            "moviename": movie_data.moviename,
            "moviedesc": movie_data.moviedesc,
            "moviegenre": movie_data.moviegenre,
            "movieyear": movie_data.movieyear,
            "updated_by": get_current_user["username"]
        }}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found or no change")

    return {"message": "Movie updated successfully"}

# allow user(admin) to delete movie
@app.delete("/movies/{movie_id}")
def delete_movies( movie_id: int, get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create movies")
    result = movie_collection.delete_one({"movie_id": movie_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    return {"message": f"Movie {movie_id} deleted successfully"}

# allow users to show all the movies
@app.get("/movies")
def get_all_movies():
    movies_cursor = movie_collection.find({}, {"_id": 0})  
    movies = list(movies_cursor)  
    return movies

# allow users to show particular movie 
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = movie_collection.find_one({"movie_id": movie_id}, {"_id": 0})  

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie

# allow user(consumer) to rent a movie
@app.post("/movies/{movie_id}/rent")
def rent_movie(movie_id: int, get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "consumer":
        raise HTTPException(status_code=403, detail="Only consumer can update movies")
    movie = movie_collection.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if not movie.get("available", True):
        raise HTTPException(status_code=400, detail="Movie is not available")
    movie_collection.update_one({"_id": movie_id}, {"$set": {"available": False}})
    rental_data = {
        "movie_id": movie_id,
        "moviename": movie["moviename"],
        "rented_by": get_current_user["username"],
        "rented_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    rental_collection.insert_one(rental_data)
    return {
        "message": f"Movie '{movie['moviename']}' successfully rented by {get_current_user['username']}."
    }

# allow user(consumer) to return a rented movie
@app.post("/movies/{movie_id}/return")
def return_movie(movie_id: int, get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "consumer":
        raise HTTPException(status_code=403, detail="Only consumer can update movies")
    movie = movie_collection.find_one({"movie_id": movie_id})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    rental = rental_collection.find_one({
        "movie_id": movie_id,
        "rented_by": get_current_user["username"],
        "return_date": {"$exists": False}
    })
    if not rental:
        raise HTTPException(status_code=400, detail="You have not rented this movie or already returned it")

    movie_collection.update_one(
        {"movie_id": movie_id},
        {"$set": {"available": True}}
    )
    rental_collection.update_one(
    {
        "movie_id": movie_id,
        "rented_by": get_current_user["username"],
        "return_date": {"$exists": False}
    },
    {"$set": {"return_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
    return {
        "message": f"Movie '{movie['moviename']}' returned successfully by {get_current_user['username']}."
    }

# consumer can view their rentals
@app.get("/users/me/rentals")
def get_my_rented_movies(get_current_user: dict = Depends(get_current_user)):
    if get_current_user["role"] != "consumer":
        raise HTTPException(status_code=403, detail="Only consumer can update movies")
    username = get_current_user["username"]
    rentals = list(rental_collection.find({
        "rented_by": username,
        "return_date": {"$exists": False}  
    }))
    if not rentals:
        return {"message": "You have no active rentals"}
    movie_names = []
    for rental in rentals:
        movie = movie_collection.find_one({"movie_id": rental["movie_id"]})
        if movie:
            movie_names.append(movie["moviename"])
    return {"your_rented_movies": movie_names}



