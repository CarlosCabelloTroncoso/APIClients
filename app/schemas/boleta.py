from pydantic import BaseModel
from datetime import datetime

class BoletaBase(BaseModel):
    id_cliente: int
    anio: int
    mes: int
    kwh_total: float
    tarifa_base: float
    cargos: float
    iva: float
    total_pagar: float
    estado: str = "emitida"

class BoletaCreate(BoletaBase):
    pass

class BoletaResponse(BoletaBase):
    id_boleta: int
    created_at: datetime

    model_config = {"from_attributes": True}
