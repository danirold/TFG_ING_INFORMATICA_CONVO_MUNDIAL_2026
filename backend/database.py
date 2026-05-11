from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#La direcccion de la base de datos (usuarios.bd) se guarda en un archivo, usamos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./usuarios.bd" 

#Creamos el "motor" usando la direccion de la base de datos
motor = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

#Creamos la sesión que se comunicará con la base de datos
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)

#La clase Base la usarán nuestros modelos (es decir, la tabla User)
Base = declarative_base()