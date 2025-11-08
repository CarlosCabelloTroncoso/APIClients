from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rut = Column(String(12), unique=True, nullable=False)
    nombre_razon = Column(String(100), nullable=False)
    email_contacto = Column(String(120))
    telefono = Column(String(20))
    direccion_facturacion = Column(String(200))
    estado = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    medidores = relationship("Medidor", back_populates="cliente")
