from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Medidor(Base):
    __tablename__ = "medidor"

    id_medidor = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo_medidor = Column(String(50), unique=True, nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    direccion_suministro = Column(String(200))
    estado = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="medidores")