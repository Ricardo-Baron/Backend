from pymongo import MongoClient

client=MongoClient("mongodb+srv://crbar32:Ricardo2823*@keyonapp.9u6wm.mongodb.net/?retryWrites=true&w=majority")

db=client.ControlAcceso_db              #->Establecemos el nombre de la base de datos
collection_name=db["Usuarios"]     #->Establecemos el nombre de la colecion
neighborhood_collection=db["Barrios"]     #->Establecemos el nombre de la colecion