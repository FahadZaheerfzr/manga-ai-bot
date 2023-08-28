import os
from dotenv import load_dotenv, find_dotenv
  
_ = load_dotenv(find_dotenv())  # read local .env file

ENVIRONMENT = os.getenv("ENVIRONMENT")
print(ENVIRONMENT)

if ENVIRONMENT == "DEVELOPMENT":
  BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
  BACKEND_URL = os.getenv("TEST_BACKEND_URL")
elif ENVIRONMENT == "PRODUCTION":
  BOT_TOKEN = os.getenv("BOT_TOKEN")
  BACKEND_URL = os.getenv("BACKEND_URL")