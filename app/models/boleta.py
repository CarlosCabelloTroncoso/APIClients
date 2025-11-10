from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, DECIMAL, UniqueConstraint
from datetime import datetime
from app.database import Base

class Boleta(Base):
    __tablename__ = "boleta"

    id_boleta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"), nullable=False)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    kwh_total = Column(Integer, nullable=False)
    tarifa_base = Column(DECIMAL(10, 2))
    cargos = Column(DECIMAL(10, 2))
    iva = Column(DECIMAL(10, 2))
    total_pagar = Column(DECIMAL(10, 2))
    estado = Column(String(20), default="emitida")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("id_cliente", "anio", "mes", name="uq_cliente_anio_mes"),)
