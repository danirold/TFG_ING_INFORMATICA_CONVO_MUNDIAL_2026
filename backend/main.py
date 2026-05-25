
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel # Para validar los datos de entrada
from typing import Optional, List

import os
import json

#Importamos lo necesario para el modelo IA de la predicción
import pandas as pd
import pickle
import numpy as np

#Importamos lo necesario para descargar el documento con la convocatoria generada
from fpdf import FPDF
from fastapi.responses import StreamingResponse
import io

# Importamos los modelos y la sesión de base de datos
import models
from database import SesionLocal, motor

#Para hashear contraseñas
from passlib.context import CryptContext

#Creamos las tablas en la base de datos (si no existen)
models.Base.metadata.create_all(bind=motor)

#Configuramos la seguridad de las contraseñas
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
def proteger_contraseña(contra):
    return pwd_context.hash(contra)
def comprobar_contraseña(contra, contra_hasheada):
    return pwd_context.verify(contra, contra_hasheada)

def crear_administrador():
    bd = SesionLocal()
    try:
        email_admin = "danielroldanserrano@gmail.com"
        # Comprobamos si ya existes en la base de datos
        admin_existente = bd.query(models.Usuario).filter(models.Usuario.email == email_admin).first()
        
        if not admin_existente:
            contraseña_admin = "daniel" 
            nuevo_admin = models.Usuario(
                email=email_admin,
                contraseña_proteg=proteger_contraseña(contraseña_admin),
                nombre="Daniel",
                primer_apellido="Roldán",
                segundo_apellido="Serrano",
                rol="administrador" 
            )
            bd.add(nuevo_admin)
            bd.commit()
    finally:
        bd.close()     
# Ejecutamos la función automáticamente al arrancar
crear_administrador()


app = FastAPI()
#Configuramos CORS, para que frontend pueda llamar a este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite a cualquiera llamar a la API
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (POST, GET, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)


ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_estaticos = os.path.join(ruta_actual, "..", "frontend", "static")
app.mount("/static", StaticFiles(directory=ruta_estaticos), name="static")

#Gestionamos la sesión de la BBDD
def obtener_bd():
    bd = SesionLocal()
    try:
        yield bd
    finally:
        bd.close()

#Modelos que esperamos recibir del frontend
#Modelo para el registro (CU 2.1)
class CrearUsuario(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: str
    email: str
    contraseña: str
#Modelo para el inicio de sesion (CU 2.2)
class IniciarSesionUsuario(BaseModel):
    email:str
    contraseña:str
#Modelo para comprobar email existente (CU 2.3)
class ComprobarEmailExiste(BaseModel):
    email:str
#Modelo para restablecer contraseña (CU 2.3)
class RestablecerContra(BaseModel):
    email:str
    nueva_contraseña: str
#Modelo para cambiar informacion del usuario (CU 2.6)
class CambiarInformacionUsuario(BaseModel):
    email_actual: str #Obligatorio para encontrar al usuario, el resto son opcionales
    nombre_nuevo: Optional[str] = None
    primer_apellido_nuevo: Optional[str] = None
    segundo_apellido_nuevo: Optional[str] = None
    email_nuevo: Optional[str] = None
    contraseña_nueva: Optional[str] = None
#Modelo para cambiar la privacidad de las notificaciones (CU 2.7)
class GestionarNotificaciones(BaseModel):
    email: str
    activadas: bool # True para notificaciones activadas, False para notificaciones desactivadas
#Modelo para eliminar cuenta de usuario (CU 2.8)
class EliminarCuenta(BaseModel):
    email: str
# Modelos para la Predicción (CU 3.4)
class FiltrosPrediccion(BaseModel):
    edad_min: Optional[int] = None
    edad_max: Optional[int] = None
    posiciones_excluidas: list[str] = []
    ligas_incluidas: list[str] = []
class PeticionPrediccion(BaseModel):
    email: str
    seleccion: str
    tipo_bd: str  #puede ser por "defecto" o "propia"
    filtros: FiltrosPrediccion

# Modelo para guardar la convocatoria en el historial (CU 3.7)
class GuardarPrediccion(BaseModel):
    email: str
    nombre_personalizado: str
    seleccion: str
    datos_jugadores: dict # Recibiremos el objeto con titulares y reservas

#Modelos para descargar el PDF de la convocatoria generada (CU 3.8)
class JugadorDescarga(BaseModel):
    nombre: str
    edad: int
    equipo: str
    posicion: str
    probabilidad: float

class PeticionDescargaPDF(BaseModel):
    seleccion: str
    modelo_predictivo: str
    titulares: List[JugadorDescarga]
    reservas: List[JugadorDescarga]


#RUTAS PARA SERVIR EL FRONTEND (HTML)
#Pantalla de anadir bd a la prediccion
@app.get("/anadir_bd_prediccion")
def servir_anadir_bd_prediccion():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "anadir_bd_prediccion.html")
    return FileResponse(ruta_html)

#Pantalla detalle historial
@app.get("/detalle_historial")
def servir_detalle_historial():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "detalle_historial.html")
    return FileResponse(ruta_html)

#Pantalla elegir seleccion
@app.get("/elegir_seleccion")
def servir_elegir_seleccion():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "elegir_seleccion.html")
    return FileResponse(ruta_html)

#Pantalla eliminar cuenta
@app.get("/eliminar_cuenta")
def servir_eliminar_cuenta():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "eliminar_cuenta.html")
    return FileResponse(ruta_html)

#Pantalla filtros convocatoria
@app.get("/filtros_convocatoria")
def servir_filtros_convocatoria():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "filtros_convocatoria.html")
    return FileResponse(ruta_html)

#Pantalla generar prediccion
@app.get("/generar_prediccion")
def servir_generar_prediccion():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "generar_prediccion.html")
    return FileResponse(ruta_html)

#Pantalla gestion de privacidad
@app.get("/gestion_privacidad")
def servir_gestion_privacidad():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "gestion_privacidad.html")
    return FileResponse(ruta_html)

#Pantalla gestion de BBDD por defecto
@app.get("/gestionar_bd_defecto")
def servir_gestionar_bd_defecto():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "gestionar_bd_defecto.html")
    return FileResponse(ruta_html)

#Pantalla gestion del modelo predictivo
@app.get("/gestionar_modelo_pred")
def servir_gestionar_modelo_pred():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "gestionar_modelo_pred.html")
    return FileResponse(ruta_html)

#Pantalla historial predicciones
@app.get("/historial_predicciones")
def servir_historial_predicciones():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "historial_predicciones.html")
    return FileResponse(ruta_html)

#Pantalla informacion personal
@app.get("/informacion_personal")
def servir_informacion_personal():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "informacion_personal.html")
    return FileResponse(ruta_html)

#Pantalla iniciar sesión administrador
@app.get("/iniciar_sesion_adm")
def servir_iniciar_sesion_adm():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "iniciar_sesion_adm.html")
    return FileResponse(ruta_html)

#Pantalla iniciar sesion usuario
@app.get("/iniciar_sesion")
def servir_iniciar_sesion_usu():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "iniciar_sesion.html")
    return FileResponse(ruta_html)

#Pantalla menu principal del administrador
@app.get("/menu_principal_adm")
def servir_menu_principal_adm():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "menu_principal_adm.html")
    return FileResponse(ruta_html)

#Pantalla menu principal de usuario
@app.get("/menu_principal")
def servir_menu_principal():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "menu_principal.html")
    return FileResponse(ruta_html)

#Pantalla mi perfil
@app.get("/mi_perfil")
def servir_mi_perfil():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "mi_perfil.html")
    return FileResponse(ruta_html)

#Pantalla de autentificación
@app.get("/")
def servir_pantalla_autentificacion():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "pantalla_autentificacion.html")
    return FileResponse(ruta_html)

#Pantalla previa a restablecer la contraseña
@app.get("/prev_restablecer_contra")
def servir_prev_restablecer_contra():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "prev_restablecer_contra.html")
    return FileResponse(ruta_html)

#Pantalla registrar usuario
@app.get("/registrar_usuario")
def servir_registrar_usuario():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "registrar_usuario.html")
    return FileResponse(ruta_html)

#Pantalla restablecer contraseña
@app.get("/restablecer_contra")
def servir_restablecer_contra():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "restablecer_contra.html")
    return FileResponse(ruta_html)

#Pantalla visualizar resultados
@app.get("/visualizar_resultados")
def servir_visualizar_resultados():
    ruta_html = os.path.join(ruta_actual, "..", "frontend", "visualizar_resultados.html")
    return FileResponse(ruta_html)


#ENDPOINTS
#Registro de usuario (CU 2.1)
@app.post("/api/auth/registrar_usuario")
def registrar_usuario(user_data: CrearUsuario, bd: Session = Depends(obtener_bd)):
    #Miramos si el email ya esta asociado a alguna cuenta existente
    bd_usuario = bd.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()
    if bd_usuario:
        raise HTTPException(status_code=400, detail="Ese email ya está asociado a un usuario registrado")

    #Protegemos la contraseña
    contraseña_protegida = proteger_contraseña(user_data.contraseña)

    #Creamos el nuevo objeto Usuario
    nuevo_usuario = models.Usuario(
        email=user_data.email,
        contraseña_proteg=contraseña_protegida,
        nombre=user_data.nombre,
        primer_apellido=user_data.primer_apellido,
        segundo_apellido=user_data.segundo_apellido,
        rol="usuario"
    )

    #Guardamos en la base de datos el nuevo usuario
    bd.add(nuevo_usuario)
    bd.commit()
    bd.refresh(nuevo_usuario)

    #Mensaje de éxito
    return {"mensaje": "¡Nuevo usuario registrado con éxito!", "email": nuevo_usuario.email}

#Iniciar sesion (CU 2.2)
@app.post("/api/auth/iniciar_sesion")
def iniciar_sesion(user_data: IniciarSesionUsuario, bd : Session = Depends(obtener_bd)):
    # Buscamos al usuario
    bd_usuario = bd.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()

    # Comprobamos que el email y la contraseña sean correctos
    if not bd_usuario or not comprobar_contraseña(user_data.contraseña, bd_usuario.contraseña_proteg):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )
    
    #Mensaje de éxito
    return {"mensaje": "¡Inicio de sesión correcto!", "email": bd_usuario.email}

#Comprobar si un email esta asociado a una cuenta existente (CU 2.3)
@app.post("/api/auth/comprobar_email")
def comprobar_email(user_data: ComprobarEmailExiste, bd: Session = Depends(obtener_bd)):
    # Buscamos si existe un usuario con ese email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()
    
    if not usuario:
        # Si no existe, devolvemos un error 404 para que el frontend lo sepa
        raise HTTPException(status_code=404, detail="Este correo no está registrado en la aplicación.")
    
    # Si existe, devolvemos éxito
    return {"mensaje": "Usuario encontrado"}

#Restablecer contraseña (CU 2.3)
@app.post("/api/auth/restablecer_contra")
def restablecer_contra(datos: RestablecerContra, bd: Session = Depends(obtener_bd)):
    # Buscamos si existe un usuario con ese email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    # Sobrescribimos la contraseña antigua con la nueva (protegida)
    usuario.contraseña_proteg = proteger_contraseña(datos.nueva_contraseña)
    bd.commit()
    
    return {"mensaje": "Contraseña restablecida correctamente."}

# Obtener información del perfil (CU 2.5)
@app.get("/api/users/obtener_perfil")
def obtener_perfil(email: str, bd: Session = Depends(obtener_bd)):
    # Buscamos al usuario por su email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Devolvemos los datos requeridos por la especificación
    return {
        "nombre": usuario.nombre,
        "primer_apellido": usuario.primer_apellido,
        "segundo_apellido": usuario.segundo_apellido,
        "email": usuario.email,
        # La contraseña está protegida en la BBDD. Enviamos un texto indicativo para cumplir el requisito visual.
        "contraseña": "********" 
    }

#Cambiar información del usuario (CU 2.6)
@app.put("/api/users/cambiar_informacion_perfil")
def cambiar_informacion_perfil(datos: CambiarInformacionUsuario, bd: Session = Depends(obtener_bd)):
    #Buscamos al usuario por su email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == datos.email_actual).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    #Actualizamos el email (solo si es uno nuevo y diferente)
    if datos.email_nuevo is not None and datos.email_nuevo != datos.email_actual:
        #Comprobamos si ya está registrado ese email en la app
        email_ocupado = bd.query(models.Usuario).filter(models.Usuario.email == datos.email_nuevo).first()
        if email_ocupado:
            raise HTTPException(status_code=400, detail="El nuevo email ya está en uso")
        usuario.email = datos.email_nuevo

    #Actualizamos el resto de datos personales (solo si se envían)
    if datos.nombre_nuevo is not None:
        usuario.nombre = datos.nombre_nuevo
    if datos.primer_apellido_nuevo is not None:
        usuario.primer_apellido = datos.primer_apellido_nuevo
    if datos.segundo_apellido_nuevo is not None:
        usuario.segundo_apellido = datos.segundo_apellido_nuevo

    #Actualizamos la contraseña (solo si se envía y no es la máscara)
    if datos.contraseña_nueva is not None:
        # Verificamos que no sea la máscara "********" ni una cadena vacía
        if datos.contraseña_nueva != "********" and datos.contraseña_nueva.strip() != "":
            usuario.contraseña_proteg = proteger_contraseña(datos.contraseña_nueva)

    #Guardamos los cambios
    bd.commit()
    bd.refresh(usuario)
    return {"mensaje": "Datos actualizados correctamente", "email": usuario.email}

# Gestión de privacidad (notificaciones) (CU 2.7)
@app.put("/api/users/gestionar_notificaciones")
def gestionar_notificaciones(datos: GestionarNotificaciones, bd: Session = Depends(obtener_bd)):
    # Buscamos al usuario por su email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizamos su preferencia
    usuario.notificaciones_activadas = datos.activadas
    
    bd.commit()
    
    estado = "activadas" if datos.activadas else "desactivadas"
    return {"mensaje": f"Notificaciones {estado} correctamente."}

#Eliminar cuenta de usuario (CU 2.8)
@app.delete("/api/users/eliminar_cuenta")
def eliminar_cuenta(datos: EliminarCuenta, bd: Session = Depends(obtener_bd)):
    # Buscamos al usuario por su email
    usuario = bd.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Lo borramos de la base de datos
    bd.delete(usuario)
    bd.commit()
    
    return {"mensaje": "Cuenta eliminada correctamente."}

#Iniciar sesion como administrador/a (CU 1.1)
@app.post("/api/auth/iniciar_sesion_admin")
def iniciar_sesion_admin(user_data: IniciarSesionUsuario, bd : Session = Depends(obtener_bd)):
    # Buscamos al usuario
    bd_usuario = bd.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()

    # Comprobamos que el email y la contraseña sean correctos
    if not bd_usuario or not comprobar_contraseña(user_data.contraseña, bd_usuario.contraseña_proteg):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )
    
    #Comprobamos si tiene el rol de administrador
    if bd_usuario.rol != "administrador":
        raise HTTPException(
            status_code=403,
            detail="Esta cuenta no tiene permisos de administrador"
        )
    
    # Mensaje de éxito
    return {"mensaje": "¡Inicio de sesión de administrador correcto!", "email": bd_usuario.email}

# Crear carpeta para guardar el dataset si no existe
os.makedirs("datos_modelo", exist_ok=True)
# Posibilidad de descargar la base de datos actual
@app.get("/api/admin/descargar_bd_defecto")
async def descargar_bd_defecto():
    ruta_archivo = "datos_modelo/dataset_defecto.csv"
    
    # Comprobamos si el archivo existe antes de intentar enviarlo
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail="No se ha encontrado la base de datos por defecto actual.")
    
    return FileResponse(
        path=ruta_archivo, 
        filename="dataset_defecto.csv", # Nombre con el que se descargará la base de datos actual
        media_type="text/csv"
    )

# Actualizar base de datos por defecto (CU 1.2)
@app.post("/api/admin/actualizar_bd_defecto")
async def actualizar_bd_defecto(archivo: UploadFile = File(...)):
    #Validamos la extensión del archivo
    if not archivo.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Formato no válido. Sube un archivo .csv")
    
    #Validamos que el nuevo archivo no esté vacío
    contenido = await archivo.read()
    if len(contenido) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    
    #Guardamos y sobrescribimos la base de datos por defecto
    ruta_destino = "datos_modelo/dataset_defecto.csv"
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    return {"mensaje": "Base de datos por defecto actualizada correctamente."}

# Actualizar modelo predictivo de IA (CU 1.3)
@app.post("/api/admin/actualizar_modelo_pred")
async def actualizar_modelo_pred(
    archivo: UploadFile = File(...),
    algoritmo: str = Form(...),
    ventana: str = Form(...),
    descripcion: str = Form(...)
):
    if not archivo.filename.endswith(".pkl"):
        raise HTTPException(status_code=400, detail="Formato no válido. Sube un archivo .pkl")
    
    contenido = await archivo.read()
    if len(contenido) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    # Guardamos el archivo con su nombre original
    nombre_original = archivo.filename
    ruta_destino = f"datos_modelo/{nombre_original}"
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    # Completamos los metadatos del modelo predictivo
    datos_metadata = {
        "archivo_original": nombre_original,
        "algoritmo": algoritmo,
        "ventana": ventana,
        "descripcion": descripcion
    }
    
    ruta_metadata = "datos_modelo/metadata_modelo.json"
    with open(ruta_metadata, "w", encoding="utf-8") as f:
        json.dump(datos_metadata, f, ensure_ascii=False, indent=4)

    return {"mensaje": f"Modelo '{nombre_original}' y metadatos actualizados correctamente."}

# Descargar plantilla de base de datos actual para el usuario (CU 3.2)
@app.get("/api/users/descargar_bd_defecto")
async def descargar_bd_usuario():
    ruta_archivo = "datos_modelo/dataset_defecto.csv"
    
    # Comprobamos si el archivo existe antes de intentar enviarlo
    if not os.path.exists(ruta_archivo):
        raise HTTPException(status_code=404, detail="No se ha encontrado la base de datos por defecto.")
    
    return FileResponse(
        path=ruta_archivo, 
        filename="dataset_actual_prediccion.csv", # Nombre con el que se descargará la base de datos actual
        media_type="text/csv"
    )
# Subir base de datos de usuario para la predicción (CU 3.2)
@app.post("/api/users/subir_bd_prediccion")
async def subir_bd_prediccion(email: str = Form(...), archivo: UploadFile = File(...)):
    #Validamos la extensión del archivo
    if not archivo.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Formato no válido. Sube un archivo .csv")
    
    #Validamos que no esté vacío
    contenido = await archivo.read()
    if len(contenido) == 0:
        raise HTTPException(status_code=400, detail="El archivo está vacío o corrupto.")
    
    #Guardamos el archivo temporalmente asociado al usuario
    os.makedirs("datos_modelo/temp", exist_ok=True)
    #Lo guardamos con el email del usuario para que no se mezcle con los de otros
    ruta_destino = f"datos_modelo/temp/{email}_dataset.csv" 
    with open(ruta_destino, "wb") as f:
        f.write(contenido)
        
    return {"mensaje": "Base de datos cargada y validada correctamente."}

# Generar predicción de convocatoria (CU 3.4)
@app.post("/api/predict/generar_convocatoria")
async def generar_prediccion(datos: PeticionPrediccion):
    try:
        # Recopilar base de datos
        if datos.tipo_bd == "defecto":
            ruta_csv = "datos_modelo/dataset_defecto.csv" 
        else:
            ruta_csv = f"datos_modelo/temp/{datos.email}_dataset.csv"
            
        if not os.path.exists(ruta_csv):
            raise HTTPException(status_code=404, detail="No se encontró la base de datos seleccionada.")
            
        try:
            df = pd.read_csv(ruta_csv, sep=";", decimal=",")
        except:
            df = pd.read_csv(ruta_csv, decimal=".")

        # Aplicar filtro de Selección Nacional
        df_filtrado = df[df["Nation"].str.contains(datos.seleccion, na=False, case=False)].copy()

        # Aplicar filtros opcionales del usuario
        if datos.filtros.edad_min is not None:
            df_filtrado = df_filtrado[df_filtrado["Age"] >= datos.filtros.edad_min]
        if datos.filtros.edad_max is not None:
            df_filtrado = df_filtrado[df_filtrado["Age"] <= datos.filtros.edad_max]
            
        for pos_excluida in datos.filtros.posiciones_excluidas:
            if pos_excluida == "POR": df_filtrado = df_filtrado[~df_filtrado["Pos"].str.contains("GK", na=False)]
            if pos_excluida == "DEF": df_filtrado = df_filtrado[~df_filtrado["Pos"].str.contains("DF", na=False)]
            if pos_excluida == "MED": df_filtrado = df_filtrado[~df_filtrado["Pos"].str.contains("MF", na=False)]
            if pos_excluida == "DEL": df_filtrado = df_filtrado[~df_filtrado["Pos"].str.contains("FW", na=False)]

        if len(datos.filtros.ligas_incluidas) > 0:
            condiciones = []
            for liga in datos.filtros.ligas_incluidas:
                if liga == "Otras":
                    ligas_conocidas = ['es La Liga', 'eng Premier League', 'it Serie A', 'de Bundesliga', 'fr Ligue 1']
                    condiciones.append(~df_filtrado["Comp"].isin(ligas_conocidas))
                else:
                    mapa_ligas = {"LaLiga": "es La Liga", "Premier League": "eng Premier League", 
                                  "Serie A": "it Serie A", "Bundesliga": "de Bundesliga", "Ligue 1": "fr Ligue 1"}
                    liga_bd = mapa_ligas.get(liga, liga)
                    condiciones.append(df_filtrado["Comp"] == liga_bd)
            
            if condiciones:
                condicion_final = condiciones[0]
                for c in condiciones[1:]:
                    condicion_final = condicion_final | c
                df_filtrado = df_filtrado[condicion_final]

        if len(df_filtrado) < 26:
            raise HTTPException(status_code=400, detail="Los filtros aplicados son demasiado estrictos. Quedan menos de 26 jugadores disponibles.")

        # Alimentar el modelo de IA
        ruta_metadata = "datos_modelo/metadata_modelo.json"
        
        # Leemos el JSON para saber qué modelo usar
        if not os.path.exists(ruta_metadata):
            raise HTTPException(status_code=404, detail="El administrador aún no ha configurado los metadatos de la IA.")
            
        with open(ruta_metadata, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        nombre_archivo_activo = metadata.get("archivo_original", "modelo_defecto.pkl")
        ruta_modelo = f"datos_modelo/{nombre_archivo_activo}"

        if not os.path.exists(ruta_modelo):
            raise HTTPException(status_code=404, detail=f"Falta el archivo del modelo ({nombre_archivo_activo}).")

        try:
            with open(ruta_modelo, "rb") as f:
                modelo_data = pickle.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fallo al cargar el modelo de IA: {str(e)}")

        rf_model = modelo_data["model"]
        preprocessor = modelo_data["preprocessor"]
        feature_names = modelo_data["feature_names"]

        # Preparamow las columnas
        df_filtrado["Pos_principal"] = df_filtrado["Pos"].str.split(",").str[0].str.strip()
        for pos in ["GK", "DF", "MF", "FW"]:
            df_filtrado[f"pos_{pos}"] = (df_filtrado["Pos_principal"] == pos).astype(int)
            
        ligas_bd = ['es La Liga', 'eng Premier League', 'it Serie A', 'de Bundesliga', 'fr Ligue 1']
        for liga in ligas_bd:
            df_filtrado[f"liga_{liga.replace(' ', '_')}"] = (df_filtrado["Comp"] == liga).astype(int)
        df_filtrado["liga_Otras"] = (~df_filtrado["Comp"].isin(ligas_bd)).astype(int)

        conv_cols = [c for c in df_filtrado.columns if "Convocatoria" in c and "1" not in c]
        conv_bin_cols = []
        for col in conv_cols:
            nombre_bin = col.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
            df_filtrado[nombre_bin] = (df_filtrado[col] == "Sí").astype(int)
            conv_bin_cols.append(nombre_bin)
        
        if len(conv_bin_cols) > 0:
            df_filtrado["experiencia_previa"] = df_filtrado[conv_bin_cols].sum(axis=1)

        for col in feature_names:
            if col not in df_filtrado.columns:
                df_filtrado[col] = 0

        X_inference = df_filtrado[feature_names].fillna(0)
        
        try:
            X_scaled = preprocessor.transform(X_inference)
            probabilidades = rf_model.predict_proba(X_scaled)[:, 1]
            df_filtrado["Probabilidad_IA"] = probabilidades
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Error en la IA: {str(e)}")

        # Aplicamos la estructura tácctica (3-8-8-7) o modo flexible
        if len(datos.filtros.posiciones_excluidas) == 0:
            top_gk = df_filtrado[df_filtrado["Pos_principal"] == "GK"].sort_values(by="Probabilidad_IA", ascending=False)
            top_df = df_filtrado[df_filtrado["Pos_principal"] == "DF"].sort_values(by="Probabilidad_IA", ascending=False)
            top_mf = df_filtrado[df_filtrado["Pos_principal"] == "MF"].sort_values(by="Probabilidad_IA", ascending=False)
            top_fw = df_filtrado[df_filtrado["Pos_principal"] == "FW"].sort_values(by="Probabilidad_IA", ascending=False)
            
            # Titulares (Los 26 elegidos)
            convocatoria_final = pd.concat([top_gk.head(3), top_df.head(8), top_mf.head(8), top_fw.head(7)])
            
            # Reservas (Los que se quedaron a las puertas)
            reservas_df = pd.concat([top_gk.iloc[3:5], top_df.iloc[8:11], top_mf.iloc[8:11], top_fw.iloc[7:10]])
            reservas_final = reservas_df.sort_values(by="Probabilidad_IA", ascending=False).head(10)
            
        else:
            # Modo flexible
            df_ordenado = df_filtrado.sort_values(by="Probabilidad_IA", ascending=False)
            convocatoria_final = df_ordenado.head(26)
            reservas_final = df_ordenado.iloc[26:36]

        # Formatear a lista de diccionarios
        # Formatear a lista de diccionarios
        def formatear_jugadores(df_jugadores):
            mapa_ligas_limpias = {
                "es La Liga": "LaLiga",
                "eng Premier League": "Premier League",
                "it Serie A": "Serie A",
                "de Bundesliga": "Bundesliga",
                "fr Ligue 1": "Ligue 1"
            }
            
            lista = []
            for _, row in df_jugadores.iterrows():
                # Extraemos la liga y la limpiamos si está en nuestro mapa
                liga_cruda = str(row["Comp"]) if pd.notna(row["Comp"]) else ""
                liga_limpia = mapa_ligas_limpias.get(liga_cruda, liga_cruda.split(" ", 1)[-1] if " " in liga_cruda else liga_cruda)

                lista.append({
                    "nombre": str(row["Player"]),
                    "edad": int(row["Age"]) if pd.notna(row["Age"]) else 0,
                    "equipo": str(row["Squad"]),
                    "liga": liga_limpia,
                    "posicion": str(row["Pos_principal"]),
                    "probabilidad": round(float(row["Probabilidad_IA"]) * 100, 1)
                })
            return lista

        # Devolvemos los datos, pero no se muestran aún
        return {
            "mensaje": "Convocatoria generada correctamente", 
            "titulares": formatear_jugadores(convocatoria_final),
            "reservas": formatear_jugadores(reservas_final)
        }

    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor al procesar la predicción.")
    
# Consultar información sobre el modelo IA (CU 3.6)
@app.get("/api/modelo/info")
async def obtener_info_modelo():
    ruta_metadata = "datos_modelo/metadata_modelo.json"
    
    try:
        # Si el archivo existe, lo leemos y lo enviamos
        if os.path.exists(ruta_metadata):
            with open(ruta_metadata, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "archivo_original": "Ningún modelo configurado",
                "algoritmo": "Desconocido",
                "ventana": "No especificada",
                "descripcion": "No se han encontrado metadatos para el modelo actual."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer la información del modelo.")
    
# Guardar convocatoria en el historial (CU 3.7)
@app.post("/api/users/guardar_convocatoria")
def guardar_convocatoria(datos: GuardarPrediccion, bd: Session = Depends(obtener_bd)):
    # Validamos que el nombre no sea vacío
    if not datos.nombre_personalizado or not datos.nombre_personalizado.strip():
        raise HTTPException(status_code=400, detail="Debes introducir un nombre para guardar la convocatoria.")

    # Validamos que el usuario no haya guardado ninguna convocatoria con ese nombre previamente
    existe = bd.query(models.HistorialPrediccion).filter(
        models.HistorialPrediccion.email_usuario == datos.email,
        models.HistorialPrediccion.nombre_personalizado == datos.nombre_personalizado
    ).first()

    if existe:
        raise HTTPException(status_code=400, detail="Ya tienes una convocatoria guardada con ese nombre.")

    try:
        # Guardamos la convocatoria en el historial de predicciones permanente
        nueva_entrada = models.HistorialPrediccion(
            email_usuario=datos.email,
            nombre_personalizado=datos.nombre_personalizado,
            seleccion=datos.seleccion,
            # Convertimos el diccionario de jugadores a texto JSON para la BBDD
            datos_json=json.dumps(datos.datos_jugadores, ensure_ascii=False)
        )
        
        bd.add(nueva_entrada)
        bd.commit()
        
        return {"mensaje": "Convocatoria guardada en tu historial correctamente."}
        
    except Exception as e:
        print(f"Error al guardar: {e}")
        raise HTTPException(status_code=500, detail="Error interno al guardar en el historial.")

# Descargar convocatoria en PDF (CU 3.8)
@app.post("/api/predict/descargar_convocatoria_pdf")
async def descargar_convocatoria_pdf(datos: PeticionDescargaPDF):
    try:
        # Creamos el objeto PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Título dividido en dos líneas explícitas para evitar cortes
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, f"INFORME DE CONVOCATORIA DE LA SELECCION {datos.seleccion.upper()}", ln=True, align="C")
        pdf.cell(0, 8, "COPA MUNDIAL DE LA FIFA 2026", ln=True, align="C")
        
        # Subtítulo (usamos multi_cell para que baje de línea si el modelo es muy largo)
        pdf.set_font("Arial", "", 10)
        subtitulo = f"Documento generado usando el Modelo Predictivo: {datos.modelo_predictivo}"
        pdf.ln(2)
        pdf.multi_cell(0, 6, subtitulo, align="C")
        pdf.ln(5)

        # Funciones auxiliares para dibujar tablas y filas
        def dibujar_cabecera_tabla():
            pdf.set_font("Arial", "B", 10)
            pdf.set_fill_color(220, 220, 220)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(60, 8, "Jugador", 1, 0, "C", True)
            pdf.cell(25, 8, "Posicion", 1, 0, "C", True)
            pdf.cell(60, 8, "Equipo", 1, 0, "C", True)
            pdf.cell(20, 8, "Edad", 1, 0, "C", True)
            pdf.cell(25, 8, "Prob.", 1, 1, "C", True)

        def dibujar_fila(jugador, es_titular):
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            
            # Eliminamos saltos de línea ocultos y limitamos a 27 caracteres
            nombre_limpio = str(jugador.nombre).replace('\n', ' ').replace('\r', '').strip()[:27]
            equipo_limpio = str(jugador.equipo).replace('\n', ' ').replace('\r', '').strip()[:27]
            
            pdf.cell(60, 8, nombre_limpio, 1, 0, "L") 
            pdf.cell(25, 8, jugador.posicion, 1, 0, "C")
            pdf.cell(60, 8, equipo_limpio, 1, 0, "L")
            pdf.cell(20, 8, str(jugador.edad), 1, 0, "C")
            
            # Color verde solo para titulares
            if es_titular:
                pdf.set_text_color(40, 167, 69)
            else:
                pdf.set_text_color(0, 0, 0)
                
            pdf.cell(25, 8, f"{jugador.probabilidad}%", 1, 1, "C")
            pdf.set_text_color(0, 0, 0) # Restaurar color negro para la siguiente celda

        # Jugadores titulares
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(180, 0, 0) # Rojo estilo España
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "LISTA DE CONVOCADOS (26 JUGADORES)", ln=True, align="C", fill=True)
        pdf.ln(2)

        pos_map = {"GK": "PORTEROS", "DF": "DEFENSAS", "MF": "CENTROCAMPISTAS", "FW": "DELANTEROS"}
        for pos_key, pos_name in pos_map.items():
            jugadores_pos = [j for j in datos.titulares if j.posicion == pos_key]
            if jugadores_pos:
                
                # Control de salto de página para no dejar títulos huérfanos
                if pdf.get_y() > 240:
                    pdf.add_page()
                
                pdf.set_font("Arial", "B", 10)
                pdf.set_fill_color(240, 240, 240)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 8, f"  {pos_name}", ln=True, fill=True)
                
                dibujar_cabecera_tabla()
                for j in jugadores_pos:
                    dibujar_fila(j, es_titular=True)
                pdf.ln(3)

        pdf.ln(2)

        # Jugadores reservas
        if pdf.get_y() > 230:
            pdf.add_page()
            
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(245, 158, 11) # Naranja/Ambar para diferenciar
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, "LISTA DE RESERVAS (10 JUGADORES)", ln=True, align="C", fill=True)
        pdf.ln(2)

        dibujar_cabecera_tabla()
        for j in datos.reservas:
            dibujar_fila(j, es_titular=False)

        # Generamos la salida
        pdf_output = pdf.output()
        
        # Nombre de archivo dinámico
        nombre_archivo = f"Convocatoria_{datos.seleccion.replace(' ', '_')}_2026.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_output),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
        )

    except Exception as e:
        print(f"Error PDF: {e}")
        raise HTTPException(status_code=500, detail="No se pudo generar el reporte PDF.")

# Obtener historial de predicciones (CU 4.1)
@app.get("/api/users/historial")
def obtener_historial(email: str, bd: Session = Depends(obtener_bd)):
    try:
        # Buscamos todas las predicciones asociadas a ese email
        historial = bd.query(models.HistorialPrediccion).filter(
            models.HistorialPrediccion.email_usuario == email
        ).order_by(models.HistorialPrediccion.fecha_guardado.desc()).all()

        # Si no hay ninguna
        if not historial:
            return [] # Mandamos lista vacía para que el frontend muestre el mensaje correspondiente

        # Devolvemos la lista
        return historial
        
    except Exception as e:
        print(f"Error al recuperar historial: {e}")
        raise HTTPException(status_code=500, detail="Error al conectar con la base de datos.")

# Borrar predicción del historial (CU 4.2)
@app.delete("/api/users/historial/{id_prediccion}")
def borrar_prediccion(id_prediccion: int, email: str, bd: Session = Depends(obtener_bd)):
    # Buscamos la predicción asegurándonos de que pertenece a ese usuario
    prediccion = bd.query(models.HistorialPrediccion).filter(
        models.HistorialPrediccion.id == id_prediccion,
        models.HistorialPrediccion.email_usuario == email
    ).first()

    if not prediccion:
        raise HTTPException(status_code=404, detail="Convocatoria no encontrada o no tienes permisos.")

    try:
        bd.delete(prediccion)
        bd.commit()
        return {"mensaje": "Convocatoria eliminada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al intentar borrar de la base de datos.")