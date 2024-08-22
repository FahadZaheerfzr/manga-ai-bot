from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv, find_dotenv
  
_ = load_dotenv(find_dotenv())  # read local .env file

ALL_POINTS = os.getenv("ALL_POINTS")

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"),tlsCAFile=certifi.where())
DB = client["MangaAI"]
