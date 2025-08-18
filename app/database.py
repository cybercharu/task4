from pymongo import MongoClient
from .config import MONGO_URI

client =  MongoClient(MONGO_URI)
db = client["customer_data"] 
collection = db["users"]
movie_collection = db["movies"]
rental_collection = db["rentals"]
