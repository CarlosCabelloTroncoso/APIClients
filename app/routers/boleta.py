from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.boleta import Boleta
from app.models.consumo import LecturaConsumo
from app.models.cliente import Cliente
from app.schemas.boleta import BoletaResponse
from app.models.medidor import Medidor

router = APIRouter(prefix="/api/boletas", tags=["Boletas"])

@router.post("/generar", response_model=BoletaResponse)
def generar_boleta(id_cliente: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente, Cliente.estado == True).first()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado o inactivo")

    hoy = datetime.now()
    anio, mes = hoy.year, hoy.month

    # Evitar duplicados
    existe = db.query(Boleta).filter(Boleta.id_cliente == id_cliente, Boleta.anio == anio, Boleta.mes == mes).first()
    if existe:
        raise HTTPException(400, "Ya existe una boleta para este mes")

    # 🔹 Obtener todos los medidores del cliente
    medidores = db.query(Medidor).filter(Medidor.id_cliente == id_cliente, Medidor.estado == True).all()
    if not medidores:
        raise HTTPException(400, "El cliente no tiene medidores activos")

    lecturas_validas = []
    for medidor in medidores:
        lecturas = (
            db.query(LecturaConsumo)
            .filter(LecturaConsumo.id_medidor == medidor.id_medidor)
            .order_by(LecturaConsumo.anio.desc(), LecturaConsumo.mes.desc())
            .limit(2)
            .all()
        )
        if len(lecturas) >= 1:
            lecturas_validas.append(lecturas)

    if not lecturas_validas:
        raise HTTPException(400, "No hay lecturas válidas para generar boleta")

    # 🔹 Calcular consumo total
    kwh_total = 0
    for lecturas in lecturas_validas:
        if len(lecturas) == 1:
            kwh_total += lecturas[0].lectura_kwh
        else:
            kwh_total += lecturas[0].lectura_kwh - lecturas[1].lectura_kwh

    if kwh_total < 0:
        kwh_total = abs(kwh_total)

    # 🔹 Calcular totales
    tarifa_base = 50.0
    cargos = 5.0
    subtotal = kwh_total * tarifa_base + cargos
    iva = round(subtotal * 0.19, 2)
    total_pagar = round(subtotal + iva, 2)

    nueva_boleta = Boleta(
        id_cliente=id_cliente,
        anio=anio,
        mes=mes,
        kwh_total=kwh_total,
        tarifa_base=tarifa_base,
        cargos=cargos,
        iva=iva,
        total_pagar=total_pagar,
        estado="emitida",
    )

    db.add(nueva_boleta)
    db.commit()
    db.refresh(nueva_boleta)

    return nueva_boleta


@router.get("/", response_model=list[BoletaResponse])
def listar_boletas(id_cliente: int | None = None, anio: int | None = None, mes: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Boleta)
    if id_cliente:
        query = query.filter(Boleta.id_cliente == id_cliente)
    if anio:
        query = query.filter(Boleta.anio == anio)
    if mes:
        query = query.filter(Boleta.mes == mes)
    return query.order_by(Boleta.created_at.desc()).all()
