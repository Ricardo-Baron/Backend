from pymongo import MongoClient
import os

#client=MongoClient("mongodb+srv://crbar32:Ricardo2823*@keyonapp.9u6wm.mongodb.net/?retryWrites=true&w=majority")

MONGO_URL = os.getenv("DATABASE_URL")  # Obtiene la URL de MongoDB desde las variables de entorno

client = MongoClient(MONGO_URL)

db=client.ControlAcceso_db              #->Establecemos el nombre de la base de datos
collection_name=db["Usuarios"]     #->Establecemos el nombre de la colecion
neighborhood_collection=db["Barrios"]     #->Establecemos el nombre de la colecion
