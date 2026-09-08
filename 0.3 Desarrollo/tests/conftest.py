"""Configuración común de las pruebas.

Las pruebas no llaman a la API de Gemini: sustituyen las tres funciones del
módulo ``ai_service`` por dobles deterministas. Así la suite se ejecuta sin
credenciales, sin costo y con resultados repetibles, que es lo que exige un
plan de pruebas. La prueba de integración real está en
``test_integracion_gemini.py`` y solo se ejecuta si se pide expresamente.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import app as aplicacion  # noqa: E402
from services import ai_service  # noqa: E402

# Vocabulario del embedding simulado: cada texto se convierte en un vector de
# frecuencias sobre estas palabras, de modo que dos textos que comparten
# términos quedan cerca en similitud coseno.
VOCABULARIO = [
    "contrato", "factura", "informe", "valor", "total", "iva", "plazo",
    "proveedor", "cliente", "hallazgo", "mantenimiento", "papeleria",
]


def embedding_simulado(texto: str, para_consulta: bool = False) -> list[float]:
    minusculas = (texto or "").lower()
    vector = [float(minusculas.count(palabra)) for palabra in VOCABULARIO]
    if not any(vector):
        vector[0] = 0.01
    return vector


def analisis_simulado(texto: str, nombre_archivo: str = "") -> dict:
    minusculas = (texto or "").lower()
    if "factura" in minusculas:
        categoria = "Factura"
        datos = [{"campo": "total", "valor": "COP 1.000.000"}, {"campo": "iva", "valor": "19%"}]
    elif "contrato" in minusculas:
        categoria = "Contrato"
        datos = [{"campo": "partes", "valor": "Empresa A y Empresa B"}, {"campo": "plazo", "valor": "12 meses"}]
    elif "informe" in minusculas:
        categoria = "Informe"
        datos = [{"campo": "periodo", "valor": "2026"}, {"campo": "hallazgos", "valor": "3"}]
    else:
        categoria = "Otro"
        datos = [{"campo": "tipo", "valor": "No indicado"}]
    return {
        "categoria": categoria,
        "resumen": f"Resumen simulado de {nombre_archivo or 'documento'}.",
        "palabras_clave": ["prueba", "simulado"],
        "datos_extraidos": datos,
        "modelo": "doble-de-prueba",
    }


def respuesta_simulada(pregunta: str, fragmentos: list[dict]) -> str:
    titulos = ", ".join(f["titulo"] for f in fragmentos[:2])
    return f"Respuesta simulada basada en [{titulos}]."


@pytest.fixture
def ia_simulada(monkeypatch):
    """Reemplaza las llamadas al proveedor de IA por dobles deterministas."""
    monkeypatch.setattr(ai_service, "analizar_documento", analisis_simulado)
    monkeypatch.setattr(ai_service, "generar_embedding", embedding_simulado)
    monkeypatch.setattr(ai_service, "responder_pregunta", respuesta_simulada)
    monkeypatch.setattr(ai_service, "disponible", lambda: True)
    return ai_service


@pytest.fixture
def app(tmp_path, ia_simulada):
    """Aplicación Flask con base de datos y almacenamiento temporales."""
    aplicacion_prueba = aplicacion.create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-de-prueba",
            "DATABASE": str(tmp_path / "prueba.sqlite3"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "WTF_CSRF_ENABLED": False,
            # Las pruebas procesan en el mismo hilo para obtener resultados
            # deterministas; el trabajador en segundo plano se prueba llamando
            # directamente a `procesamiento.procesar_pendientes`.
            "PROCESAR_EN_SEGUNDO_PLANO": False,
        }
    )
    Path(aplicacion_prueba.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    yield aplicacion_prueba


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sesion(client):
    """Registra e inicia sesión con el primer usuario (administrador)."""

    def _entrar(correo="admin@demo.com", clave="clave123", nombre="Administrador"):
        client.post(
            "/registro",
            data={"nombre": nombre, "correo": correo, "clave": clave},
            follow_redirects=True,
        )
        return client.post(
            "/login", data={"correo": correo, "clave": clave}, follow_redirects=True
        )

    return _entrar
