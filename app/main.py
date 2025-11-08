from fastapi import FastAPI

from app.routers.cliente import router as cliente_router
from app.routers.medidor import router as medidor_router
from app.routers.consumo import router as consumo_router
from app.routers.boleta import router as boleta_router

from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(cliente_router)
app.include_router(medidor_router)
app.include_router(consumo_router)
app.include_router(boleta_router)

@app.get("/")
def home():
    return {"status": "API Funcionando ✅"}
