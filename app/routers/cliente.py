from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, ClientesPaginated

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get("/", response_model=ClientesPaginated)
def listar_clientes(
    buscar: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Cliente).filter(Cliente.estado == 1)  # 👈 Clave

    if buscar:
        query = query.filter(
            (Cliente.nombre_razon.ilike(f"%{buscar}%")) |
            (Cliente.rut.ilike(f"%{buscar}%"))
        )

    total = query.count()
    total_paginas = (total + limit - 1) // limit

    clientes = query.offset((page - 1) * limit).limit(limit).all()

    return ClientesPaginated(
        total_registros=total,
        pagina_actual=page,
        por_pagina=limit,
        total_paginas=total_paginas,
        clientes=clientes
    )




@router.get("/{id_cliente}", response_model=ClienteResponse)
def obtener_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteResponse)
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):
    # Validar RUT único
    existe = db.query(Cliente).filter(Cliente.rut == data.rut).first()
    if existe:
        raise HTTPException(400, "El RUT ya está registrado")

    cliente = Cliente(**data.dict())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{id_cliente}", response_model=ClienteResponse)
def actualizar_cliente(id_cliente: int, data: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    for field, value in data.dict().items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{id_cliente}")
def eliminar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
    if not cliente:
        raise HTTPException(404, "Cliente no encontrado")

    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado definitivamente"}