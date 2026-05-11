# TFG_ING_INFORMATICA_CONVO_MUNDIAL_2026

Aplicación predictiva de convocatorias de selecciones de fútbol: Estudio de caso para España en la Copa Mundial de la FIFA 2026

Este proyecto es un Trabajo de Fin de Grado que utiliza algoritmos de Inteligencia Artificial y Aprendizaje Automático para predecir la lista de la Selección Española de Fútbol de la Copa Mundial de la FIFA 2026.

## Objetivo del Proyecto
El sistema se divide en dos fases:
1. **Fase de investigación:** Entrenamiento y evaluación de cuatro modelos predictivos (Random Forest, XGBoost, Regresión Logística y SVM) para capturar con la mayor precisión posible el criterio del seleccionador nacional, Luis de la Fuente.
2. **Aplicación web:** Una plataforma interactiva que permite automatizar la predicción, modificar el *dataset* en tiempo real para simular escenarios hipotéticos y generar informes en PDF.

## Estructura del Repositorio
- `/Backend`: Código del servidor desarrollado con **FastAPI**, base de datos SQLite y los modelos de IA entrenados (`.pkl`/`.json`).
- `/Frontend`: Interfaz de usuario interactiva (HTML, CSS, JS) para la visualización y gestión de datos.
- `/PruebaDatasetFutbol`: Scripts de limpieza de datos en Python y *datasets* originales/depurados.
- `/Memoria`: Recursos e imágenes utilizados en la redacción del documento final del TFG.

## Cómo iniciar la aplicación (con un entorno local)
Para descargar y ejecutar este proyecto en tu propia máquina, asegúrate de tener instalado [Python](https://www.python.org/) y [Git](https://git-scm.com/). Luego, sigue estos pasos desde tu terminal:

### 1. Descargar el proyecto
Clona el repositorio en tu ordenador y entra en la carpeta del proyecto:
(bash) git clone [https://github.com/danirold/TFG_ING_INFORMATICA_CONVO_MUNDIAL_2026.git](https://github.com/danirold/TFG_ING_INFORMATICA_CONVO_MUNDIAL_2026.git)
(bash) cd TFG_ING_INFORMATICA_CONVO_MUNDIAL_2026

### 2. Configurar el backend
Navega hacia la carpeta del servidor donde se encuentra la lógica de la aplicación:
(bash) cd Backend

### 3. Crear y activar el entorno virtual
Es fundamental crear un entorno virtual:
Windows: (bash) python -m venv venv
         (bash) .\venv\Scripts\activate
macOS/Linux: (bash) python3 -m venv venv
             (bash) source venv/bin/activate

### 4. Instalar las dependencias
Con el entorno virtual activado (aparecerá el prefijo (venv) en tu terminal), instala todas las librerías necesarias:
(bash) pip install -r requirements.txt

### 5. Iniciar el servidor FastAPI
Una vez instaladas las dependencias, arranca el servidor:
(bash) uvicorn main:app --reload

### 6.Acceder a la plataforma
Abre tu navegador web y dirígete a la siguiente dirección local:
(bash) http://127.0.0.1:8000
