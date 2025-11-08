from fastapi import APIRouter

router = APIRouter(prefix="/lecturas", tags=["Lecturas"])

@router.get("/")
def listar_lecturas():
    return {"msg": "Listar lecturas funciona ✅"}
