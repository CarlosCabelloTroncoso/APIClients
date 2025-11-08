from pydantic import BaseModel

class MedidorBase(BaseModel):
    codigo_medidor: str
    id_cliente: int
    direccion_suministro: str | None = None
    estado: bool = True

class MedidorCreate(MedidorBase):
    pass

class MedidorUpdate(BaseModel):
    direccion_suministro: str | None = None
    estado: bool | None = None

class MedidorResponse(MedidorBase):
    id_medidor: int

    class Config:
        from_attributes = True
