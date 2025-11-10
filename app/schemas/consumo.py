from pydantic import BaseModel
from datetime import datetime

class LecturaBase(BaseModel):
    id_medidor: int
    anio: int
    mes: int
    lectura_kwh: int
    observacion: str | None = None

class LecturaCreate(LecturaBase):
    pass

class LecturaResponse(LecturaBase):
    id_lectura: int
    created_at: datetime

    class Config:
        from_attributes = True
