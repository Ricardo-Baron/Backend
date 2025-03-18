from fastapi import FastAPI
from routes.rutas import endpoint
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app=FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:8081"],  # Permitir solicitudes desde React
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

app.include_router(endpoint)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)