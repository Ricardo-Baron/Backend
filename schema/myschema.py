import secrets
import string
#------------------->FUNCION QUE ARMA UN DICCIONARIO CON UN SOLO ELEMENTO DEL TIPO CLASS
def individual_serial(item)-> dict:
    return{
        "id":str(item["_id"]),
        "nombre":item["name"],
        "dni":item["dni"],
        "barrios":item["barrios"],
        "mail":item["mail"],
        "password":item["password"],
        "passwordQR":item["passwordQR"],
        "nivel":item["nivel"],
        "fechaInicial":item["fechaInicial"],
        "fechaFinal":item["fechaFinal"]
    }
#------------------>FUNCION QUE COLOCA EN UNA LISTA LOS ELEMENTOS  DE TIPO CLASS
def list_serial(items)->list:
    return [individual_serial(item) for item in items]



#------------------>FUNCION QUE ARMA UN DICCIONARIO CON UN SOLO ELEMENTO DEL TIPO CLASS
def individual_serial_Barrio(item)->dict:
    return {
        "id":str(item["_id"]),
        "nombre":item["nombre"],
        "tipo":item["tipo"],
        "descripcion":item["descripcion"],
        "direccion":item["direccion"],
        "fechaInicio":item["fechaInicio"],
        "fechaFin":item["fechaFin"],
        "coordenadas":item["coordenadas"],
        "usuariosConRoles":item["usuariosConRoles"]
    }
#--------------->FUNCION QUE ARMA UNA LISTA  DE DICCIONARIOS DE LOS ITEMS DADO-------->
def list_serial_Barrios(items)->list:
    return [individual_serial_Barrio(item) for item in items ]




#------------------>En esta funcion se recive un diccionario y en funcion de los datos se arma una contraseña
def passQR(usuario):
            # Definir los caracteres permitidos y la longitud de la contraseña
    caracteres = string.ascii_letters + string.digits + string.punctuation
    
    longitud = 12

            # Crear una lista para almacenar los caracteres aleatorios
    caracteres_aleatorios = []

            # Usar un bucle for tradicional para llenar la lista
    for _ in range(longitud):
        caracter_aleatorio = secrets.choice(caracteres)  # Seleccionar un carácter aleatorio
        caracteres_aleatorios.append(caracter_aleatorio)  # Agregarlo a la lista

            # Unir los caracteres en un string
    contrasena = ''.join(caracteres_aleatorios)

    print("Contraseña generada:", contrasena)

    usuario["passwordQR"]=contrasena
    return usuario