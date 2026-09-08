"""Orquestador del flujo documental.

Implementa la secuencia que exige la guía del proyecto:

    archivo -> extracción de contenido -> procesamiento IA -> análisis
    -> almacenamiento de resultados -> búsqueda/consulta -> respuesta

Este módulo cubre del primer al quinto paso. La búsqueda y la consulta viven
en las rutas de la aplicación y en ``services/rag.py``.

Además expone un trabajador en segundo plano que va procesando los documentos
en estado ``Pendiente`` uno por uno, de modo que una carga masiva no obligue al
usuario a esperar con la página bloqueada.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

from services import ai_service, rag
from services.extractor import ErrorExtraccion, dividir_en_fragmentos, extraer_texto

ESTADO_PENDIENTE = "Pendiente"
ESTADO_PROCESADO = "Procesado"
ESTADO_ERROR = "Error"

_candado = threading.Lock()
_trabajador: threading.Thread | None = None


def procesar_documento(db, documento_id: int, ruta_archivo: str | Path) -> dict:
    """Ejecuta el flujo completo sobre un documento ya almacenado.

    Nunca propaga excepciones de IA o de extracción: cualquier falla se guarda
    en ``estado_procesamiento`` y ``error_procesamiento`` para que quede
    trazada en la interfaz y en la bitácora.

    Devuelve ``{"estado": ..., "detalle": ...}``.
    """
    try:
        texto, origen = _obtener_texto(ruta_archivo)
    except ErrorExtraccion as exc:
        return _marcar_error(db, documento_id, f"Extracción: {exc}")
    except ai_service.ErrorIA as exc:
        return _marcar_error(db, documento_id, f"Transcripción con IA: {exc}")

    try:
        analisis = ai_service.analizar_documento(texto, Path(ruta_archivo).name)
    except ai_service.ErrorIA as exc:
        # El texto extraído sí se guarda: la búsqueda por contenido funciona
        # aunque el análisis de IA haya fallado.
        db.execute(
            "UPDATE documentos SET contenido_extraido = ? WHERE id = ?", (texto, documento_id)
        )
        return _marcar_error(db, documento_id, f"IA: {exc}")

    db.execute(
        """
        UPDATE documentos
        SET contenido_extraido = ?,
            categoria = ?,
            resumen = ?,
            palabras_clave = ?,
            datos_extraidos = ?,
            modelo_ia = ?,
            estado_procesamiento = ?,
            error_procesamiento = NULL,
            procesado_en = CURRENT_TIMESTAMP,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            texto,
            analisis["categoria"],
            analisis["resumen"],
            ", ".join(analisis["palabras_clave"]),
            json.dumps(analisis["datos_extraidos"], ensure_ascii=False),
            analisis["modelo"],
            ESTADO_PROCESADO,
            documento_id,
        ),
    )

    try:
        indexados = rag.indexar_documento(db, documento_id, dividir_en_fragmentos(texto))
    except ai_service.ErrorIA as exc:
        # El documento queda clasificado y resumido, pero sin índice semántico.
        return _marcar_error(db, documento_id, f"Indexación semántica: {exc}", conservar=True)

    return {
        "estado": ESTADO_PROCESADO,
        "detalle": (
            f"Clasificado como {analisis['categoria']}, "
            f"{len(analisis['datos_extraidos'])} datos extraídos, "
            f"{indexados} fragmentos indexados{origen}."
        ),
    }


def _obtener_texto(ruta_archivo: str | Path) -> tuple[str, str]:
    """Obtiene el texto del archivo, con la IA como respaldo.

    Primero intenta la extracción local, que es gratuita e inmediata. Si el
    archivo no tiene texto recuperable (un PDF escaneado o una imagen) y el
    modelo puede leer ese formato, se transcribe con IA.

    Devuelve el texto y una nota sobre su origen para la bitácora.
    """
    try:
        return extraer_texto(ruta_archivo), ""
    except ErrorExtraccion:
        if not ai_service.admite_vision(ruta_archivo):
            raise
    return ai_service.transcribir_archivo(ruta_archivo), " (texto obtenido por OCR)"


def _marcar_error(db, documento_id: int, detalle: str, conservar: bool = False) -> dict:
    """Registra el fallo en el documento sin interrumpir la aplicación."""
    estado = ESTADO_PROCESADO if conservar else ESTADO_ERROR
    db.execute(
        """
        UPDATE documentos
        SET estado_procesamiento = ?,
            error_procesamiento = ?,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (estado, detalle[:500], documento_id),
    )
    return {"estado": ESTADO_ERROR, "detalle": detalle}


# ---------------------------------------------------------------------------
# Procesamiento por lotes
# ---------------------------------------------------------------------------


def contar_pendientes(db) -> int:
    return db.execute(
        "SELECT COUNT(*) AS total FROM documentos WHERE estado_procesamiento = ?",
        (ESTADO_PENDIENTE,),
    ).fetchone()["total"]


def procesar_pendientes(base_datos: str, carpeta_archivos: str, limite: int = 0) -> dict:
    """Procesa los documentos en estado `Pendiente`, uno por uno.

    Abre su propia conexión, por lo que puede ejecutarse desde un hilo aparte.
    ``limite`` en 0 significa procesar todos los que haya. Devuelve el conteo de
    procesados y fallidos.
    """
    procesados = fallidos = 0
    while limite == 0 or procesados + fallidos < limite:
        conexion = sqlite3.connect(base_datos, timeout=30)
        conexion.row_factory = sqlite3.Row
        try:
            fila = conexion.execute(
                """
                SELECT id, nombre_original, nombre_almacenado
                FROM documentos
                WHERE estado_procesamiento = ?
                ORDER BY id
                LIMIT 1
                """,
                (ESTADO_PENDIENTE,),
            ).fetchone()
            if fila is None:
                break

            ruta = Path(carpeta_archivos) / fila["nombre_almacenado"]
            try:
                resultado = procesar_documento(conexion, fila["id"], ruta)
            except Exception as exc:  # nunca dejar el documento en Pendiente
                resultado = _marcar_error(conexion, fila["id"], f"Error inesperado: {exc}")

            conexion.execute(
                """
                INSERT INTO bitacora (usuario_id, accion, detalle, nivel)
                VALUES (NULL, 'PROCESAR_DOCUMENTO', ?, ?)
                """,
                (
                    f"{fila['nombre_original']}: {resultado['detalle']}"[:500],
                    "INFO" if resultado["estado"] == ESTADO_PROCESADO else "ERROR",
                ),
            )
            conexion.commit()
            if resultado["estado"] == ESTADO_PROCESADO:
                procesados += 1
            else:
                fallidos += 1
        finally:
            conexion.close()

    return {"procesados": procesados, "fallidos": fallidos}


def iniciar_trabajador(base_datos: str, carpeta_archivos: str) -> bool:
    """Lanza en segundo plano el procesamiento de los pendientes.

    Si ya hay un trabajador activo no se crea otro: el que está corriendo
    tomará también los documentos recién cargados. Devuelve ``True`` cuando
    arranca un hilo nuevo.
    """
    global _trabajador
    with _candado:
        if _trabajador is not None and _trabajador.is_alive():
            return False
        _trabajador = threading.Thread(
            target=procesar_pendientes,
            args=(base_datos, carpeta_archivos),
            name="procesamiento-documental",
            daemon=True,
        )
        _trabajador.start()
        return True


def trabajador_activo() -> bool:
    return _trabajador is not None and _trabajador.is_alive()
