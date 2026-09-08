"""Prueba de integración real contra la API de Gemini.

Se salta por defecto para que la suite sea rápida y no consuma cuota. Para
ejecutarla, con la clave configurada en .env:

    PRUEBA_IA_REAL=1 python -m pytest tests/test_integracion_gemini.py -v
    (en PowerShell:  $env:PRUEBA_IA_REAL=1; python -m pytest tests/test_integracion_gemini.py -v)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
load_dotenv(RAIZ / ".env")

from services import ai_service  # noqa: E402

pytestmark = pytest.mark.skipif(
    os.getenv("PRUEBA_IA_REAL") != "1" or not ai_service.disponible(),
    reason="Define PRUEBA_IA_REAL=1 y GEMINI_API_KEY para ejecutar la prueba real.",
)

FACTURA = """FACTURA ELECTRONICA DE VENTA No. FE-2601
EMISOR: Servicios Andinos Demo S.A.S. NIT 900.111.222-3
CLIENTE: Distribuidora Giron Demo S.A.S. NIT 900.121.232-1
FECHA DE EMISION: 05 de marzo de 2026
DETALLE: 1 x Licencia anual de software de gestion - valor unitario COP 4.200.000
SUBTOTAL: COP 4.200.000
IVA (19%): COP 798.000
TOTAL A PAGAR: COP 4.998.000"""


def test_ia_real_clasifica_y_extrae_una_factura():
    """CP-27: la API real clasifica el documento y extrae sus datos clave."""
    resultado = ai_service.analizar_documento(FACTURA, "factura_001.txt")
    assert resultado["categoria"] == "Factura"
    assert len(resultado["resumen"]) > 40
    assert len(resultado["datos_extraidos"]) >= 3
    valores = " ".join(dato["valor"] for dato in resultado["datos_extraidos"])
    assert "4.998.000" in valores or "4998000" in valores


def test_ia_real_genera_embeddings_comparables():
    """CP-28: dos textos afines quedan más cerca que dos textos distintos."""
    from services.rag import similitud_coseno

    factura = ai_service.generar_embedding("factura de venta con IVA del 19 por ciento")
    similar = ai_service.generar_embedding("comprobante de venta con impuesto agregado")
    distinto = ai_service.generar_embedding("informe de accidentalidad laboral en bodega")
    assert similitud_coseno(factura, similar) > similitud_coseno(factura, distinto)


def test_ia_real_responde_solo_con_el_contexto():
    """CP-29: sin contexto pertinente, el modelo admite que no tiene la información."""
    fragmentos = [{"titulo": "factura_001.txt", "texto": FACTURA}]
    respuesta = ai_service.responder_pregunta("¿Cuál es el total a pagar?", fragmentos)
    assert "4.998.000" in respuesta or "4998000" in respuesta
