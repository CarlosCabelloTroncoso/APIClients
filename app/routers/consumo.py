from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.consumo import LecturaConsumo
from app.models.medidor import Medidor
from app.schemas.consumo import LecturaCreate, LecturaResponse

router = APIRouter(prefix="/api/lecturas", tags=["Lecturas"])

@router.post("/", response_model=LecturaResponse)
def crear_lectura(data: LecturaCreate, db: Session = Depends(get_db)):
    # Verificar si el medidor existe
    medidor = db.query(Medidor).filter(Medidor.id_medidor == data.id_medidor).first()
    if not medidor:
        raise HTTPException(400, "El medidor no existe")

    existe = db.query(LecturaConsumo).filter(
        LecturaConsumo.id_medidor == data.id_medidor,
        LecturaConsumo.anio == data.anio,
        LecturaConsumo.mes == data.mes
    ).first()
    if existe:
        raise HTTPException(400, "Ya existe una lectura para este medidor en este mes")

    # Obtener lectura anterior
    lectura_anterior = db.query(LecturaConsumo).filter(
        LecturaConsumo.id_medidor == data.id_medidor
    ).order_by(LecturaConsumo.anio.desc(), LecturaConsumo.mes.desc()).first()

    if lectura_anterior:
        consumo_kwh = data.lectura_kwh - lectura_anterior.lectura_kwh
        if consumo_kwh < 0:
            raise HTTPException(400, "La lectura actual no puede ser menor a la anterior")
    else:
        consumo_kwh = 0  # primera lectura

    nueva_lectura = LecturaConsumo(**data.dict())
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    return nueva_lectura


@router.get("/", response_model=list[LecturaResponse])
def listar_lecturas(
    id_medidor: int,
    anio: int | None = None,
    mes: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(LecturaConsumo).filter(LecturaConsumo.id_medidor == id_medidor)

    if anio:
        query = query.filter(LecturaConsumo.anio == anio)
    if mes:
        query = query.filter(LecturaConsumo.mes == mes)

    return query.order_by(LecturaConsumo.anio, LecturaConsumo.mes).all()
