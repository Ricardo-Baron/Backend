from fastapi import APIRouter, Response
from models.modelo import User, BarrioBase,LoginRequest
from config.database import collection_name, neighborhood_collection
from schema.myschema import list_serial, individual_serial,passQR,list_serial_Barrios, individual_serial_Barrio
from starlette.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from bson import ObjectId
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import qrcode
import io
import uuid

# Configuración del JWT
SECRET_KEY = "KeyOnAppGroup"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Expiración del token en minutos

# Manejo de contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer para manejar el token en el header "Authorization"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

endpoint=APIRouter()

#------------Funcion que encripta la contraseña--------------------
def get_password_hash(password: str) -> str:
    
    """Genera un hash seguro para la contraseña"""
    return pwd_context.hash(password)

def create_jwt_token(data: dict):
    """Genera un token JWT con los datos del usuario"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # Agrega expiración
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    """Verifica si la contraseña ingresada es correcta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash seguro para la contraseña"""
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Obtiene los datos del usuario a partir del token"""
    print("Obtiene los datos del usuario a partir del token")
    print(token)
    print("--------------")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("El payload es: ")
        print(payload)
        return {"dni": payload["sub"], "role": payload["role"]}
    except JWTError as e:
        print(e)
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
  #------>ESTA FUNCION SOLO PERMITE QUE INGRESEN LOS USUARIOS CON CIERTOS ROLES      
def require_role(allowed_roles: list):
    """Middleware para restringir acceso a ciertos roles"""
    def role_checker(usuario: dict = Depends(get_current_user)):
        if usuario["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permisos para acceder a este recurso")
        return usuario
    return role_checker

#*************<<<<<--------------ENDPOINTS------------------------>>>>>>>************
# GET REQUEST METHOD---> logueo con email y contraseña
@endpoint.post("/login/")
async def login_user(datos:LoginRequest):
    print("--Ingreso a  login--")
    usuario=collection_name.find_one({"mail":datos.email})
    print(datos.email)
    print(datos.password)
    print(usuario["password"])
    print(verify_password(datos.password, usuario["password"]))
    print(pwd_context.hash(datos.password))

    if not usuario or not verify_password(datos.password, usuario["password"]):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    datosUsuario=individual_serial(usuario)
    # Si es válido, generamos el token
    token = create_jwt_token({"sub": str(usuario["dni"]), "role": usuario["nivel"]})
    print(token)
    #respuesta = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    #print(respuesta)
    return {"nombre":datosUsuario["nombre"],"token": token, "token_type": "bearer"}
    '''
    print("Ingreso!!!!!!!")
    usuario=collection_name.find_one({"password":datos.password})
    print(datos)
    print(datos.password)
    email=datos.email
    datosUsuario=individual_serial(usuario)
    
    if email==datosUsuario["mail"]:
        respuesta={"nombre":datosUsuario["nombre"],"token":datosUsuario["dni"], "mail":datosUsuario["mail"]}
        print(respuesta)
        return respuesta
    else:
        return  HTTP_400_BAD_REQUEST
    '''
# GET REQUEST METHOD---->-Obtiene todos los usuarios
@endpoint.get('/')
async def get_all(usuario: dict = Depends(get_current_user)):
    print(f"Bienvenido, tu DNI es {usuario['dni']} y tu rol es {usuario['role']}")
    usuarios=list_serial(collection_name.find())
    return usuarios

#--->GET REQUEST----->Obtiene los grupos a los que pertenece el usuario
@endpoint.get('/api/users/groups')
async def get_grupos(usuario: dict = Depends(get_current_user)): #get_current_user  permite acceder a cualquier usuario logueado
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no autenticado")
        
    print(f"El usuario es:")
    print( usuario)
    
    dni=usuario["dni"]
    respuesta=[]
    usuario=collection_name.find({"dni":int(dni)})
    #print(f"Usuarios es: {usuario}")
    usuario_dict=list_serial(usuario)
    print(usuario_dict)
    tamanio=len(usuario_dict)
    print(tamanio)
    
    for n in range(0,tamanio):
        barrio=neighborhood_collection.find_one({"nombre":usuario_dict[n]["barrios"]})
        #print("El barrio es:")
        #print(usuario_dict[n]["barrios"])
        #print(barrio)

        datosBarrio=individual_serial_Barrio(barrio)
        print(datosBarrio)
        id_object=datosBarrio["id"]
        respuesta.append({"nombre":usuario_dict[n]["barrios"], "nivel":usuario_dict[n]["nivel"],"_id":id_object,
                          "description":datosBarrio["descripcion"],"name":datosBarrio["nombre"]},)
    
    print(respuesta)
    return respuesta


# POST REQUEST METHOD--->Se agrega un nuevo usuario
#@endpoint.post('/')

@endpoint.post("/api/users/create")
async def create_neighborhood(user:User,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
#async def add_user(user:User): 
    new_user=dict(user)
    print(f"El user es {User}")
    existeBarrio=neighborhood_collection.find_one({"nombre":new_user["barrios"]})
    #print(f"el tipo es {type(User)}")
    #print(f"new_user es {new_user}")
    #print(f"El barrio es: ")
    #print(new_user["barrios"][0])
    #existeBarrio=await get_barrio(new_user["barrios"]) #Devuelve un diccionario con los datos del barrio
    #barrioActualizado=dict(exiteBarrio)
    #print(type(existeBarrio))
    print(f"el barrio es {existeBarrio}")
    #if existeBarrio is not None:
           # new_user=passQR(new_user)
            #collection_name.insert_one(new_user)
    #else:
          # return HTTP_400_BAD_REQUEST
    if existeBarrio is not None:
        password_hash=get_password_hash(new_user["password"])
        new_user["password"]=password_hash
        result=collection_name.insert_one(new_user)    #Creamos el Usuario
        print(f"el resultes {result}")
        inserted_id=result.inserted_id
        print(f"El id: ", inserted_id)
        #existeBarrio["integrantes"].append(new_user["dni"]) #agregamos el dni a el campo integrantes del barrio
        print(f"los datos son ")
        
        datos={"id":str(inserted_id),"name":new_user["name"],"dni":new_user["dni"],"nivel":new_user["nivel"],"fechaInicial":new_user["fechaInicial"],"fechaFinal":new_user["fechaFinal"]}
        print(datos)
        existeBarrio["usuariosConRoles"].append(datos)
        await actualizar_barrio(new_user["barrios"], existeBarrio)
        return HTTP_201_CREATED
    else:
        return HTTP_400_BAD_REQUEST
    

#----DELETE REQUEST METHOD-------->Borrado de usuarios
@endpoint.delete("/api/user/delete/{UserToDelete}")
async def delete_user(UserToDelete:str,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
    print("Entrando en Delete user--")
    print(UserToDelete)
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(UserToDelete)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    user=collection_name.find_one({"_id": object_id})
    userData=individual_serial(user)
    print(userData)
    barrio=userData["barrios"]      #Buscamos el barrio del cual es miembro

    ElBarrio = neighborhood_collection.find_one({"nombre": barrio})
    BarrioData=individual_serial_Barrio(ElBarrio)
    print(BarrioData)
    tamanio=len(BarrioData["usuariosConRoles"])
    print(tamanio)
    for n in range(0,tamanio):
        print(UserToDelete )
        print(BarrioData["usuariosConRoles"][n])
        if UserToDelete  == BarrioData["usuariosConRoles"][n]["id"]:
            print(UserToDelete)
            eliminado=BarrioData["usuariosConRoles"].pop(n)
            print(f"El eliminado es {eliminado}")
            collection_name.find_one_and_delete({"_id": object_id})
    
    print("El barrio despues de eliminar usuario:")
    print(BarrioData)
    barrio_Id=BarrioData["id"]
    try:
        # Convertir el ID a ObjectId
        objectB_id = ObjectId(barrio_Id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    try :
        neighborhood_collection.find_one_and_update({"_id": objectB_id},{"$set":BarrioData})
        return HTTP_201_CREATED
    except Exception as e:
        print (e)
        return HTTP_400_BAD_REQUEST

# PUT REQUEST METHOD----------->Actualiza el usuario
@endpoint.put("/api/users/edit/{userId}")
async def actualizar_user(userId:str, user:User, usuario: dict = Depends(require_role(["administrador", "moderador"]))):#user:User):
    print("Entrando en Actualizar_User---")
    print(userId)
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(userId)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    # Convertir el modelo a diccionario
    user_data = user.model_dump()  # Para FastAPI 0.95+
    # neighborhood_data = neighborhood.dict()  # Para versiones anteriores
    print(user_data)

    oldUser=collection_name.find_one({"_id": object_id}) #Obtenemos los datos del usuario antes de actualizar
    oldDataUser=individual_serial(oldUser)
    if oldDataUser["password"]!=user_data["password"]:
        password_hash=get_password_hash(user_data["password"])
        user_data["password"]=password_hash
        print(password_hash)

    collection_name.find_one_and_update({"_id": object_id},{"$set":user_data})
    newDataUser={"id":userId,"name":user_data["name"],"dni":user_data["dni"],"nivel":user_data["nivel"],"fechaInicial":user_data["fechaInicial"],"fechaFinal":user_data["fechaFinal"]}
    
    barrio=neighborhood_collection.find_one({"nombre": user_data["barrios"]})
    BarrioData=individual_serial_Barrio(barrio)
    print(BarrioData)
    tamanio=len(BarrioData["usuariosConRoles"])
    print(tamanio)
    for n in range(0,tamanio):
        print(userId )
        print(BarrioData["usuariosConRoles"][n])
        if userId  == BarrioData["usuariosConRoles"][n]["id"]:
            print(userId)
            eliminado=BarrioData["usuariosConRoles"].pop(n)
            print(f"El eliminado es {eliminado}")
            BarrioData["usuariosConRoles"].append(newDataUser)
            print(BarrioData)
    if eliminado is not None:
        try :
            neighborhood_collection.find_one_and_update({"nombre": user_data["barrios"]},{"$set":BarrioData})
            return HTTP_201_CREATED
        except Exception as e:
            print (e)
            return HTTP_400_BAD_REQUEST
    else:
        return HTTP_400_BAD_REQUEST


#GET REQUEST METHOD----->Obtiene los datos de un usuario
@endpoint.get("/api/users/{userId}")
async def get_DataUser(userId:str):#,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
    print("Entrando en GetDataUser user--")
    print(userId)
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(userId)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    try :
        user=collection_name.find_one({"_id": object_id})
        userData=individual_serial(user)
        print(userData)
        return userData
    except Exception as e:
        print (e)
        return HTTP_400_BAD_REQUEST

# GET REQUEST METHOD: Generacion de QR
@endpoint.get("/api/generate_qr/{userId}")
async def generar_QR(userId:str):

    token = userId+"-"+str(uuid.uuid4())  # Genera un ID único
    #url = f"https://misitio.com/acceso?token={token}"
    
    qr = qrcode.make(token)  
    print(f"El token: {token}")
    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)
    
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(userId)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    try :
        user=collection_name.find_one({"_id": object_id})
        userData=individual_serial(user)
        userData["name"]=userData.pop("nombre")
        print(userData)
        userData["passwordQR"]=token
        collection_name.find_one_and_update({"_id": object_id},{"$set":userData})
    except Exception as e:
        print (e)
        return HTTP_400_BAD_REQUEST
    

    return Response(content=img_io.getvalue(), media_type="image/png")

# GET REQUEST METHOD:Permite al ingresar actualizar la contraseña de QR
@endpoint.get("/{passwordQR}")
async def ingreso_user(passwordQR:str):
    try:
        usuario=individual_serial(collection_name.find_one({"passwordQR":passwordQR}))
        new_user=passQR(usuario)
        collection_name.find_one_and_update({"dni":int(new_user["dni"])}, {"$set":new_user})
        return HTTP_204_NO_CONTENT
    except Exception as e:
        print(e)
        return  HTTP_400_BAD_REQUEST
#-------------------BASE DE DATOS DE BARRIOS--------------------<<<<<
# POST REQUEST METHOD --------->Creamos un Barrio
#@endpoint.post("/barrios/")
#async def create_neighborhood(neighborhood:BarrioBase):
@endpoint.post("/api/groups/create")
async def create_neighborhood(neighborhood:BarrioBase,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
    print("----Creacion de barrio")
    barrioDict=dict(neighborhood)
    print(neighborhood)
    resultado=neighborhood_collection.insert_one(barrioDict)
    if resultado is not None:
        return HTTP_201_CREATED
    else:
        return  HTTP_204_NO_CONTENT

# <<--------GET  REQUEST METHOD-------->Obtiene  los datos del barrio
#@endpoint.get("/grupos/{groupid}")
#async  def get_barrio_datos(groupid:str):
@endpoint.get("/api/groupsDetails/{groupid}")
async def get_barrio(groupid: str,usuario: dict = Depends(get_current_user)):
    print("Entrando en get_barrio_datos--")
    print(groupid)
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(groupid)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")

    
    # Buscar el barrio en la base de datos
    barrio = neighborhood_collection.find_one({"_id": object_id})

    if not barrio:
        raise HTTPException(status_code=404, detail="Barrio no encontrado")
    
    datosBarrio=individual_serial_Barrio(barrio)
    print(datosBarrio)
    tamanio=len(datosBarrio["usuariosConRoles"])
    print(tamanio)
    usuarios=[]
    for n in range(0,tamanio):
        datos=datosBarrio["usuariosConRoles"][n]
        print(datos)
        usuarios.append(datos)
    datosBarrio["usuariosConRoles"]=usuarios
    print(datosBarrio)
    
    return datosBarrio

# DELETE REQUEST  METHOD-------->Borramos el dato de un Barrio
#@endpoint.delete("/barrio/{nombre}")
#async def delete_barrio(nombre:str):
@endpoint.delete("/api/groups/delete/{groupid}")
async def delete_barrio(groupid: str,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
#async def delete_barrio(groupid:str):
    print("Entrando a Delete Group------")
    print(f"group Id {groupid}")
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(groupid)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    barrio=neighborhood_collection.find_one({"_id": object_id})
    datosBarrio=individual_serial_Barrio(barrio)
    nombreBarrio=datosBarrio["nombre"]
    miembrosBarrio=collection_name.delete_many({"barrios":nombreBarrio})
    #print(f"Usuarios es: {miembrosBarrio}")
    #usuario_dict=list_serial(miembrosBarrio)

    try :
        neighborhood_collection.find_one_and_delete({"_id": object_id})
        return HTTP_201_CREATED
    except Exception as e:
        print (e)
        return HTTP_400_BAD_REQUEST

# PUT REQUEST METHOD---------->Actualizamos barrio
@endpoint.put("/api/groups/edit/{groupId}")
async def actualizar_barrio(groupId: str, neighborhood:BarrioBase,usuario: dict = Depends(require_role(["administrador", "moderador"]))):
    print("Entrando a Edit Group------")
    print(f"group Id {groupId}")
    try:
        # Convertir el ID a ObjectId
        object_id = ObjectId(groupId)
    except Exception:
        raise HTTPException(status_code=400, detail="ID inválido")
    
    BarrioViejo=neighborhood_collection.find_one({"_id": object_id})
    print("---->barrio Viejo")
    print(BarrioViejo)
    
    # Convertir el modelo a diccionario
    neighborhood_data = neighborhood.model_dump()  # Para FastAPI 0.95+
    # neighborhood_data = neighborhood.dict()  # Para versiones anteriores
    print(neighborhood)
    print(neighborhood_data)
    neighborhood_data["usuariosConRoles"]=BarrioViejo["usuariosConRoles"]
    try :
        neighborhood_collection.find_one_and_update({"_id": object_id},{"$set":neighborhood_data})
        return HTTP_201_CREATED
    except Exception as e:
        print (e)
        return HTTP_400_BAD_REQUEST
    

# GET REQUEST METHOD ------>Obtiene todos los barrios
@endpoint.get("/barrios/")
async def get_all_barrios():
    barrios=list_serial_Barrios(neighborhood_collection.find())
    return barrios

# GET REQUEST METHOD -------->Obtiene los datos de un barrio  
'''
@endpoint.get("/barrio/{nombre}")
async def get_barrio(nombre:str):
    
    elBarrio=None
    print(f"@Endpoint barrio entregado {nombre}")
    barrioBuscado=neighborhood_collection.find_one({"nombre":nombre})
    print(f" @Endpoint el BarrioBuscado: {barrioBuscado}")
    if barrioBuscado is not None:
        elBarrio=individual_serial_Barrio(barrioBuscado)
        print(f" @Endpoint elBarrio: {elBarrio}")
    return elBarrio
'''



# PUT REQUEST METHOD---------->Actualizamos barrio
@endpoint.put("/barrio/{nombre}")
async def actualizar_barrio(nombre:str, neighborhood:BarrioBase):
    neighborhood_collection.find_one_and_update({"nombre":nombre},{"$set":dict(neighborhood)})

# GET REQUEST METHOD--------->Obtendremos los integrantes de cada barrio
@endpoint.get("/integrantes/{dni}")
async def get_integrantes(dni:int):
    miembro=[]
    barrios=list_serial_Barrios(neighborhood_collection.find())
    print(barrios)
    for barrio in barrios: 
        if dni in barrio["integrantes"]:
            miembro.append(barrio["nombre"])
    usuario=individual_serial(collection_name.find_one({"dni":int(dni)}))
    print(usuario)
    usuario["accesos"]=miembro
    print(usuario)

    return usuario

    