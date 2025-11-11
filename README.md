# CGE API

Esta API fue desarrollada con **FastAPI** y **SQLAlchemy**, y permite la gestión de clientes, medidores, lecturas y boletas eléctricas.  
Incluye endpoints para crear, listar, actualizar y eliminar registros, además de generar boletas en formato PDF.

## Requisitos previos

- Python 3.10 o superior  
- pip (gestor de paquetes de Python)  
- Entorno virtual recomendado

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/usuario/cge-api.git
   cd cge-api
   ```

2. Crear y activar un entorno virtual:

   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/Mac:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar la base de datos en el archivo `database.py` (por defecto usa SQLite, pero puede adaptarse a MySQL o PostgreSQL).

5. Ejecutar la API:

   ```bash
   uvicorn main:app --reload
   ```

6. Abrir el navegador en:

   ```
   http://127.0.0.1:8000/docs
   ```

   Desde allí se puede probar y visualizar toda la documentación generada automáticamente por FastAPI.

## Estructura del proyecto

```
cge-api/
│
├── main.py               # Punto de entrada de la aplicación
├── models/               # Modelos de base de datos
├── routers/              # Rutas de la API (clientes, medidores, lecturas, boletas)
├── database.py           # Configuración de la conexión a la base de datos
├── schemas/              # Validaciones con Pydantic
├── utils/                # Funciones auxiliares (por ejemplo, generación de PDF)
└── requirements.txt      # Dependencias del proyecto
```

## Dependencias principales

- fastapi  
- uvicorn  
- sqlalchemy  
- pydantic  
- python-multipart  
- reportlab  
- python-dateutil  
