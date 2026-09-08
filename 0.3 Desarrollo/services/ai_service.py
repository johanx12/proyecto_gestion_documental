"""Integración con la API de Google Gemini.

Este módulo concentra las tres llamadas que el sistema hace al proveedor de IA:

1. ``analizar_documento``  -> clasificación, resumen y extracción de datos.
2. ``generar_embedding``   -> vector semántico de un texto (búsqueda y RAG).
3. ``responder_pregunta``  -> respuesta en lenguaje natural con fuentes citadas.

La clave nunca se escribe en el código: se lee de la variable de entorno
``GEMINI_API_KEY``. Si no existe, las funciones lanzan ``ErrorIA`` y la
aplicación registra el documento con estado ``Error`` sin caerse.
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import requests

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
CATEGORIAS = ("Contrato", "Factura", "Informe", "Otro")

# Máximo de caracteres enviados al modelo por documento. Evita exceder la
# ventana de contexto y controla el costo de cada llamada.
LIMITE_CARACTERES = 12000

# Formatos que el modelo puede leer directamente como archivo. Se usan cuando la
# extracción local no obtiene texto: PDF escaneados e imágenes (OCR).
TIPOS_VISION = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

# Tope del archivo que se envía en línea a la API.
LIMITE_VISION_BYTES = 12 * 1024 * 1024


class ErrorIA(RuntimeError):
    """Falla controlada de la integración con el proveedor de IA."""


def modelo_texto() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def modelo_embedding() -> str:
    return os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")


def dimension_embedding() -> int:
    return int(os.getenv("GEMINI_EMBEDDING_DIM", "768"))


def api_key() -> str | None:
    clave = os.getenv("GEMINI_API_KEY", "").strip()
    return clave or None


def disponible() -> bool:
    """Indica si hay credencial configurada para llamar al proveedor."""
    return api_key() is not None


def estado_integracion() -> dict[str, str]:
    """Estado que se muestra en la interfaz y en el chequeo de salud."""
    activo = disponible()
    return {
        "proveedor": "Google Gemini (API generativelanguage)",
        "modelo_texto": modelo_texto(),
        "modelo_embedding": f"{modelo_embedding()} ({dimension_embedding()} dimensiones)",
        "estado": "Activo" if activo else "Sin clave configurada (GEMINI_API_KEY)",
        "tecnica": "Extracción de texto, prompting con JSON estructurado y RAG por similitud coseno",
    }


def _llamar(ruta: str, payload: dict, intentos: int = 3, timeout: int = 90) -> dict:
    """POST a la API con reintentos ante saturación temporal del servicio."""
    clave = api_key()
    if clave is None:
        raise ErrorIA(
            "No hay GEMINI_API_KEY configurada. Copia .env.example a .env y agrega tu clave."
        )

    ultimo_error = ""
    for intento in range(intentos):
        try:
            respuesta = requests.post(
                f"{API_BASE}/{ruta}",
                headers={"x-goog-api-key": clave, "Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            ultimo_error = f"Error de red: {exc}"
        else:
            if respuesta.status_code == 200:
                return respuesta.json()
            ultimo_error = f"HTTP {respuesta.status_code}: {respuesta.text[:200]}"
            # 429, 500 y 503 son transitorios (cuota o saturación); el resto no.
            if respuesta.status_code not in (429, 500, 503):
                break
        time.sleep(2 * (intento + 1))

    raise ErrorIA(f"La API de Gemini no respondió correctamente. {ultimo_error}")


def _texto_de(respuesta: dict) -> str:
    """Concatena las partes de texto de la respuesta del modelo."""
    candidatos = respuesta.get("candidates") or []
    if not candidatos:
        raise ErrorIA("El modelo no devolvió candidatos (posible bloqueo de seguridad).")
    partes = candidatos[0].get("content", {}).get("parts") or []
    texto = "".join(parte.get("text", "") for parte in partes).strip()
    if not texto:
        raise ErrorIA("El modelo devolvió una respuesta vacía.")
    return texto


ESQUEMA_ANALISIS = {
    "type": "OBJECT",
    "properties": {
        "categoria": {"type": "STRING", "enum": list(CATEGORIAS)},
        "resumen": {"type": "STRING"},
        "palabras_clave": {"type": "ARRAY", "items": {"type": "STRING"}},
        "datos_extraidos": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "campo": {"type": "STRING"},
                    "valor": {"type": "STRING"},
                },
                "required": ["campo", "valor"],
            },
        },
    },
    "required": ["categoria", "resumen", "palabras_clave", "datos_extraidos"],
}

INSTRUCCION_ANALISIS = """Eres un analista documental de una empresa colombiana.
Analiza el documento y responde SOLO con el JSON pedido, en español.

1. categoria: elige exactamente una entre Contrato, Factura, Informe u Otro.
2. resumen: entre 40 y 80 palabras, concreto, sin inventar datos.
3. palabras_clave: entre 3 y 6 términos presentes en el documento.
4. datos_extraidos: entre 4 y 8 pares campo/valor con la información clave
   segun el tipo de documento:
   - Contrato: partes, objeto, valor, plazo, fecha de firma.
   - Factura: numero, emisor, cliente, fecha, subtotal, IVA, total.
   - Informe: titulo, autor o area, periodo, hallazgos, conclusion.
   Si un dato no aparece en el texto, escribe "No indicado". Nunca lo inventes.
"""


def analizar_documento(texto: str, nombre_archivo: str = "") -> dict:
    """Clasifica, resume y extrae datos de un documento ya convertido a texto.

    Devuelve un diccionario con ``categoria``, ``resumen``, ``palabras_clave``
    y ``datos_extraidos``. Lanza ``ErrorIA`` si el proveedor falla.
    """
    contenido = (texto or "").strip()
    if not contenido:
        raise ErrorIA("El documento no contiene texto legible para analizar.")

    prompt = (
        f"{INSTRUCCION_ANALISIS}\n\nNombre del archivo: {nombre_archivo or 'sin nombre'}\n"
        f"--- CONTENIDO DEL DOCUMENTO ---\n{contenido[:LIMITE_CARACTERES]}"
    )
    respuesta = _llamar(
        f"{modelo_texto()}:generateContent",
        {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": ESQUEMA_ANALISIS,
                "temperature": 0.2,
            },
        },
    )

    try:
        datos = json.loads(_texto_de(respuesta))
    except json.JSONDecodeError as exc:
        raise ErrorIA(f"El modelo devolvió un JSON inválido: {exc}") from exc

    categoria = datos.get("categoria", "Otro")
    return {
        "categoria": categoria if categoria in CATEGORIAS else "Otro",
        "resumen": (datos.get("resumen") or "").strip(),
        "palabras_clave": [
            str(p).strip() for p in datos.get("palabras_clave", []) if str(p).strip()
        ],
        "datos_extraidos": [
            {"campo": str(d.get("campo", "")).strip(), "valor": str(d.get("valor", "")).strip()}
            for d in datos.get("datos_extraidos", [])
            if str(d.get("campo", "")).strip()
        ],
        "modelo": modelo_texto(),
    }


def admite_vision(ruta: str | Path) -> bool:
    """Indica si el modelo puede leer este archivo directamente."""
    return Path(ruta).suffix.lower() in TIPOS_VISION


def transcribir_archivo(ruta: str | Path) -> str:
    """Envía el archivo al modelo y devuelve su texto (OCR).

    Se usa cuando la extracción local no obtiene texto: PDF escaneados sin capa
    de texto e imágenes de documentos.
    """
    ruta = Path(ruta)
    tipo = TIPOS_VISION.get(ruta.suffix.lower())
    if tipo is None:
        raise ErrorIA(f"El modelo no puede leer archivos {ruta.suffix} directamente.")

    datos = ruta.read_bytes()
    if len(datos) > LIMITE_VISION_BYTES:
        raise ErrorIA(
            f"El archivo pesa {len(datos) // (1024 * 1024)} MB y supera el máximo "
            f"de {LIMITE_VISION_BYTES // (1024 * 1024)} MB para la transcripción."
        )

    respuesta = _llamar(
        f"{modelo_texto()}:generateContent",
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": tipo,
                                "data": base64.b64encode(datos).decode("ascii"),
                            }
                        },
                        {
                            "text": (
                                "Transcribe el contenido de este documento a texto plano, "
                                "respetando el orden de lectura y conservando cifras, fechas "
                                "y nombres tal como aparecen. No agregues comentarios ni "
                                "interpretaciones: devuelve únicamente la transcripción."
                            )
                        },
                    ],
                }
            ],
            "generationConfig": {"temperature": 0},
        },
        timeout=180,
    )
    try:
        return _texto_de(respuesta)
    except ErrorIA as exc:
        raise ErrorIA(
            f"No se pudo transcribir el archivo, puede estar en blanco o ilegible. {exc}"
        ) from exc


def generar_embedding(texto: str, para_consulta: bool = False) -> list[float]:
    """Convierte un texto en un vector semántico calculado por la API."""
    contenido = (texto or "").strip()
    if not contenido:
        raise ErrorIA("No se puede generar un vector de un texto vacío.")

    respuesta = _llamar(
        f"{modelo_embedding()}:embedContent",
        {
            "model": f"models/{modelo_embedding()}",
            "content": {"parts": [{"text": contenido[:LIMITE_CARACTERES]}]},
            "taskType": "RETRIEVAL_QUERY" if para_consulta else "RETRIEVAL_DOCUMENT",
            "outputDimensionality": dimension_embedding(),
        },
        timeout=60,
    )
    valores = respuesta.get("embedding", {}).get("values")
    if not valores:
        raise ErrorIA("La API no devolvió el vector del texto.")
    return [float(v) for v in valores]


def responder_pregunta(pregunta: str, fragmentos: list[dict]) -> str:
    """Responde en lenguaje natural usando solo los fragmentos recuperados.

    ``fragmentos`` es la lista que entrega el módulo RAG: cada elemento tiene
    ``titulo`` y ``texto``. El prompt obliga al modelo a citar los documentos y
    a admitir cuando la información no está en el repositorio.
    """
    if not fragmentos:
        raise ErrorIA("No hay fragmentos de contexto para responder.")

    contexto = "\n\n".join(
        f"[Documento {i + 1}: {f['titulo']}]\n{f['texto']}" for i, f in enumerate(fragmentos)
    )
    prompt = (
        "Eres el asistente documental de una empresa. Responde la pregunta usando "
        "UNICAMENTE los fragmentos entregados.\n"
        "Reglas: responde en español, máximo 120 palabras; cita entre corchetes el "
        "nombre de los documentos que sustentan la respuesta; si los fragmentos no "
        "contienen la información, di exactamente: No encontré esa información en "
        "los documentos del repositorio.\n\n"
        f"--- FRAGMENTOS ---\n{contexto}\n\n--- PREGUNTA ---\n{pregunta}"
    )
    respuesta = _llamar(
        f"{modelo_texto()}:generateContent",
        {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        },
    )
    return _texto_de(respuesta)
