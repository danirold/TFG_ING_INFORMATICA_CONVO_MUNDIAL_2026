from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database import Base # Importamos Base, creada en database.py
from datetime import datetime

#Definimos la clase "Usuario"
class Usuario(Base):
    __tablename__ = "usuarios" 

    id = Column(Integer, primary_key=True, index=True) 
    email = Column(String, unique=True, index=True) #unique = true, para que dos usuarios no puedan tener el mismo email
    contraseña_proteg = Column(String) 
    nombre = Column(String)
    primer_apellido = Column(String)
    segundo_apellido = Column(String)
    rol = Column(String, default="usuario") #Hay que distinguir entre usuario o administrador
    notificaciones_activadas = Column(Boolean, default=False)  

# Nueva tabla para el Historial de predicciones (CU 3.7 y 4.1)
class HistorialPrediccion(Base):
    __tablename__ = "historial_predicciones"

    id = Column(Integer, primary_key=True, index=True)
    email_usuario = Column(String, index=True) # Para saber a qué usuario pertenece
    nombre_personalizado = Column(String, index=True)
    seleccion = Column(String)
    fecha_guardado = Column(DateTime, default=datetime.now)
    datos_json = Column(Text) # Aquí guardaremos toda la lista de jugadores (titulares y reservas)