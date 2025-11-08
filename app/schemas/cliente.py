from pydantic import BaseModel
from datetime import datetime

class ClienteBase(BaseModel):
    rut: str
    nombre_razon: str
    email_contacto: str | None = None
    telefono: str | None = None
    direccion_facturacion: str | None = None
    estado: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre_razon: str | None = None
    email_contacto: str | None = None
    telefono: str | None = None
    direccion_facturacion: str | None = None
    estado: bool | None = None

class ClienteResponse(ClienteBase):
    id_cliente: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ClientesPaginated(BaseModel):
    total_registros: int
    pagina_actual: int
    por_pagina: int
    total_paginas: int
    clientes: list[ClienteResponse]

    model_config = {"from_attributes": True}
