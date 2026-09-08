"""Recuperación semántica (RAG) sobre los fragmentos indexados.

El sistema no usa una base vectorial externa: guarda cada vector como JSON en
la tabla ``fragmentos`` de SQLite y calcula la similitud coseno en Python. Para
el volumen académico del proyecto (decenas de documentos) es suficiente,
reproducible y no agrega infraestructura al despliegue.
"""

from __future__ import annotations

import json
import math

from services import ai_service

TOP_K = 5


def similitud_coseno(a: list[float], b: list[float]) -> float:
    """Similitud coseno entre dos vectores del mismo tamaño."""
    if not a or not b or len(a) != len(b):
        return 0.0
    producto = sum(x * y for x, y in zip(a, b))
    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return producto / (norma_a * norma_b)


def buscar_fragmentos(db, pregunta: str, filas_permitidas: list, top_k: int = TOP_K) -> list[dict]:
    """Devuelve los fragmentos más parecidos a la pregunta.

    ``filas_permitidas`` son los fragmentos que el usuario puede consultar
    (ya filtrados por propietario en la consulta SQL), de modo que el control
    de acceso ocurre antes del cálculo de similitud.
    """
    if not filas_permitidas:
        return []

    vector_pregunta = ai_service.generar_embedding(pregunta, para_consulta=True)

    puntuados = []
    for fila in filas_permitidas:
        try:
            vector = json.loads(fila["vector"])
        except (TypeError, json.JSONDecodeError):
            continue
        puntuados.append(
            {
                "documento_id": fila["documento_id"],
                "titulo": fila["titulo"],
                "texto": fila["texto"],
                "similitud": similitud_coseno(vector_pregunta, vector),
            }
        )

    puntuados.sort(key=lambda f: f["similitud"], reverse=True)
    return puntuados[:top_k]


def indexar_documento(db, documento_id: int, fragmentos: list[str], maximo: int = 12) -> int:
    """Genera y guarda el vector de cada fragmento de un documento.

    Reemplaza los fragmentos anteriores para que un reprocesamiento no
    duplique el índice. Devuelve cuántos fragmentos quedaron indexados.
    """
    db.execute("DELETE FROM fragmentos WHERE documento_id = ?", (documento_id,))
    guardados = 0
    for orden, texto in enumerate(fragmentos[:maximo]):
        vector = ai_service.generar_embedding(texto)
        db.execute(
            """
            INSERT INTO fragmentos (documento_id, orden, texto, vector)
            VALUES (?, ?, ?, ?)
            """,
            (documento_id, orden, texto, json.dumps(vector)),
        )
        guardados += 1
    return guardados
