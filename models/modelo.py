from pydantic import BaseModel
from  typing import List, Optional
from bson import ObjectId

class User(BaseModel):
    name:str
    dni:int
    mail:str
    password:str
    passwordQR:Optional [str]=None
    nivel:str
    fechaInicial:Optional [str]=None
    fechaFinal:Optional [str]=None
    barrios: str

    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True  # Permite tipos arbitrarios
    }

class UsuarioConRol(BaseModel):
    _id: str
    dni: int
    name: str
    nivel: str
    fechaInicial: Optional[str] = None
    fechaFinal: Optional[str] = None
    

class BarrioBase(BaseModel):
    nombre:str
    tipo:str
    direccion:str
    descripcion:str
    fechaInicio:Optional[str] = None
    fechaFin:Optional[str] = None
    coordenadas:str
    usuariosConRoles:List[UsuarioConRol]=[]

    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True  # Permite tipos arbitrarios
    }

class LoginRequest(BaseModel):
    email: str
    password: str

