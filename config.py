import os
from dotenv import load_dotenv, find_dotenv
  
_ = load_dotenv(find_dotenv())  # read local .env file

BOT_TOKEN = os.getenv("BOT_TOKEN")
