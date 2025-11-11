from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UniqueConstraint
from datetime import datetime
from app.database import Base
from typing import Optional


class LecturaConsumo(Base):
    __tablename__ = "lectura_consumo"

    id_lectura = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_medidor = Column(Integer, ForeignKey("medidor.id_medidor"), nullable=False)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    lectura_kwh = Column(Integer, nullable=False)
    observacion = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("id_medidor", "anio", "mes", name="uq_medidor_anio_mes"),)

    
