import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import FileResponse
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


# Generar PDF
@router.get("/{id_boleta}/pdf")
def generar_pdf_boleta(id_boleta: int, db: Session = Depends(get_db)):
    boleta = db.query(Boleta).filter(Boleta.id_boleta == id_boleta).first()
    if not boleta:
        raise HTTPException(404, "Boleta no encontrada")

    cliente = db.query(Cliente).filter(Cliente.id_cliente == boleta.id_cliente).first()
    if not cliente:
        raise HTTPException(404, "Cliente asociado no encontrado")

    os.makedirs("pdfs", exist_ok=True)
    filename = f"boleta_{id_boleta}.pdf"
    filepath = os.path.join("pdfs", filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    margin = 50

    # Encabezado con color
    c.setFillColorRGB(0.2, 0.5, 0.9)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, height - 50, "Boleta de Electricidad")
    c.setFont("Helvetica", 10)
    c.drawString(margin, height - 65, "Factura electrónica de suministro eléctrico")

    # Título del documento
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - 110, f"Boleta de Electricidad N° {boleta.id_boleta}")

    # Datos del cliente
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 140, "Datos del Cliente:")
    c.setFont("Helvetica", 11)
    c.drawString(margin, height - 160, f"Nombre/Razón Social: {cliente.nombre_razon}")
    c.drawString(margin, height - 175, f"RUT: {cliente.rut}")
    c.drawString(margin, height - 190, f"Dirección: {cliente.direccion_facturacion}")
    c.drawString(margin, height - 205, f"Email: {cliente.email_contacto}")
    c.drawString(margin, height - 220, f"Teléfono: {cliente.telefono}")

    # Datos del período
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 250, "Periodo de Facturación:")
    c.setFont("Helvetica", 11)
    c.drawString(margin, height - 270, f"Año: {boleta.anio}     Mes: {boleta.mes}")
    c.drawString(margin, height - 285, f"Fecha de emisión: {boleta.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

    # Detalle de consumo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 320, "Detalle de Consumo:")
    c.setFont("Helvetica", 11)
    c.drawString(margin, height - 340, f"Consumo total: {boleta.kwh_total} kWh")
    c.drawString(margin, height - 355, f"Tarifa base: ${boleta.tarifa_base} por kWh")
    c.drawString(margin, height - 370, f"Cargos adicionales: ${boleta.cargos}")

    # Totales
    y = height - 420
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Resumen de Pago:")

    c.setFont("Helvetica", 11)
    c.drawString(margin, y - 20, f"Subtotal: ${round(boleta.kwh_total * boleta.tarifa_base + boleta.cargos, 2)}")
    c.drawString(margin, y - 35, f"IVA (19%): ${boleta.iva}")

    # Total destacado
    c.setFillColor(colors.lightgrey)
    c.rect(margin - 5, y - 75, 200, 30, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y - 65, f"TOTAL A PAGAR: ${boleta.total_pagar}")

    # Estado
    c.setFont("Helvetica", 10)
    c.drawString(margin, y - 110, f"Estado: {boleta.estado.upper()}")

    # Footer
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 40, "Gracias por preferirnos")

    c.save()

    return FileResponse(filepath, media_type="application/pdf", filename=filename)
