import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()  

MONGO_URI = os.getenv("MONGO_URI")
client =  MongoClient(MONGO_URI)
db = client["customer_data"] 
collection = db["users"]
movie_collection = db["movies"]
rental_collection = db["rentals"]
