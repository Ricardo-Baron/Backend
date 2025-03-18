from fastapi import FastAPI
from pymongo.mongo_client import MongoClient

app=FastAPI()


url = "mongodb+srv://crbar32:Ricardo2823*@keyonapp.9u6wm.mongodb.net/?retryWrites=true&w=majority&appName=KeyOnApp"

# Create a new client and connect to the server
client = MongoClient(url)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)