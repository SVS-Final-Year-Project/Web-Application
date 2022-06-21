import pyrebase
import dotenv
import os

dotenv.load_dotenv('.env')

config = {
    "apiKey": os.environ["API_KEY"],
    "authDomain": os.environ["AUTH_DOMAIN"],
    "projectId": os.environ["PROJECT_ID"],
    "storageBucket": os.environ["STORAGE_BUCKET"],
    "messagingSenderId": os.environ["MESSAGING_SENDER_ID"],
    "appId": os.environ["APP_ID"],
    "databaseURL": os.environ["DATABASE_URL"] 
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()
