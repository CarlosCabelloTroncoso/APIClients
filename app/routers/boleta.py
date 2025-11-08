from fastapi import APIRouter

router = APIRouter(prefix="/boletas", tags=["Boletas"])

@router.get("/")
def listar_boletas():
    return {"msg": "Listar boletas funciona ✅"}
