"""Carga el repositorio de prueba y ejecuta el flujo de IA sobre cada archivo.

Deja el sistema listo para la sustentación: crea el usuario administrador, el
repositorio corporativo y procesa los 30 documentos de ``11_repositorio_pruebas``.

Uso:
    python scripts/cargar_demo.py                 # los 30 documentos
    python scripts/cargar_demo.py --limite 6      # solo 6 (prueba rápida)
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path
from uuid import uuid4

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from werkzeug.security import generate_password_hash  # noqa: E402

import app as aplicacion  # noqa: E402
from services import procesamiento  # noqa: E402

ORIGEN = RAIZ.parent / "11_repositorio_pruebas" / "datos_prueba"
CORREO_DEMO = "admin@demo.com"
CLAVE_DEMO = "admin123"

# Segunda cuenta, con rol `usuario`, para demostrar el aislamiento por
# propietario: no ve los repositorios del administrador.
CORREO_USUARIO = "usuario@demo.com"
CLAVE_USUARIO = "usuario123"


def documentos_disponibles(limite: int | None) -> list[Path]:
    archivos = sorted(
        ruta
        for carpeta in sorted(ORIGEN.iterdir())
        if carpeta.is_dir()
        for ruta in sorted(carpeta.iterdir())
        if ruta.suffix.lower() in {".txt", ".docx", ".pdf"}
    )
    return archivos[:limite] if limite is not None else archivos


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga documentos de demostración")
    parser.add_argument("--limite", type=int, default=None, help="cantidad máxima de documentos")
    parser.add_argument("--pausa", type=float, default=1.0, help="segundos entre documentos")
    argumentos = parser.parse_args()

    if not ORIGEN.exists():
        print(f"No se encontró la carpeta de documentos: {ORIGEN}")
        return 1

    with aplicacion.app.app_context():
        db = aplicacion.get_db()

        usuario = db.execute(
            "SELECT id FROM usuarios WHERE correo = ?", (CORREO_DEMO,)
        ).fetchone()
        if usuario is None:
            cursor = db.execute(
                """
                INSERT INTO usuarios (nombre, correo, clave_hash, rol)
                VALUES (?, ?, ?, 'administrador')
                """,
                ("Administrador Demo", CORREO_DEMO, generate_password_hash(CLAVE_DEMO)),
            )
            usuario_id = cursor.lastrowid
            print(f"Usuario creado: {CORREO_DEMO} / {CLAVE_DEMO}")
        else:
            usuario_id = usuario["id"]
            print(f"Usuario existente: {CORREO_DEMO}")

        if db.execute(
            "SELECT id FROM usuarios WHERE correo = ?", (CORREO_USUARIO,)
        ).fetchone() is None:
            db.execute(
                """
                INSERT INTO usuarios (nombre, correo, clave_hash, rol)
                VALUES (?, ?, ?, 'usuario')
                """,
                ("Usuario Demo", CORREO_USUARIO, generate_password_hash(CLAVE_USUARIO)),
            )
            print(f"Usuario creado: {CORREO_USUARIO} / {CLAVE_USUARIO} (rol usuario)")

        repositorio = db.execute(
            "SELECT id FROM repositorios WHERE nombre = ?", ("Archivo corporativo",)
        ).fetchone()
        if repositorio is None:
            cursor = db.execute(
                """
                INSERT INTO repositorios (nombre, descripcion, propietario_id)
                VALUES (?, ?, ?)
                """,
                (
                    "Archivo corporativo",
                    "Contratos, facturas e informes de la empresa demo.",
                    usuario_id,
                ),
            )
            repositorio_id = cursor.lastrowid
        else:
            repositorio_id = repositorio["id"]
        db.commit()

        carpeta_destino = Path(aplicacion.app.config["UPLOAD_FOLDER"])
        carpeta_destino.mkdir(parents=True, exist_ok=True)

        procesados = fallidos = omitidos = 0
        archivos = documentos_disponibles(argumentos.limite)
        print(f"Documentos a procesar: {len(archivos)}\n")

        for indice, origen in enumerate(archivos, start=1):
            ya_existe = db.execute(
                """
                SELECT id FROM documentos
                WHERE repositorio_id = ? AND nombre_original = ?
                """,
                (repositorio_id, origen.name),
            ).fetchone()
            if ya_existe:
                omitidos += 1
                print(f"[{indice:02d}/{len(archivos)}] {origen.name}: ya estaba cargado")
                continue

            nombre_almacenado = f"{uuid4().hex}{origen.suffix.lower()}"
            destino = carpeta_destino / nombre_almacenado
            shutil.copyfile(origen, destino)

            cursor = db.execute(
                """
                INSERT INTO documentos (
                    repositorio_id, titulo, descripcion, categoria, nombre_original,
                    nombre_almacenado, tipo_mime, tamano_bytes, estado_procesamiento, creado_por
                ) VALUES (?, ?, ?, 'Otro', ?, ?, ?, ?, ?, ?)
                """,
                (
                    repositorio_id,
                    origen.stem.replace("_", " ").capitalize(),
                    f"Documento de prueba de la carpeta {origen.parent.name}.",
                    origen.name,
                    nombre_almacenado,
                    "application/octet-stream",
                    destino.stat().st_size,
                    procesamiento.ESTADO_PENDIENTE,
                    usuario_id,
                ),
            )
            documento_id = cursor.lastrowid
            db.commit()

            resultado = procesamiento.procesar_documento(db, documento_id, destino)
            db.execute(
                """
                INSERT INTO bitacora (usuario_id, accion, detalle, nivel)
                VALUES (?, 'PROCESAR_DOCUMENTO', ?, ?)
                """,
                (
                    usuario_id,
                    f"{origen.name}: {resultado['detalle']}"[:500],
                    "INFO" if resultado["estado"] == procesamiento.ESTADO_PROCESADO else "ERROR",
                ),
            )
            db.commit()

            if resultado["estado"] == procesamiento.ESTADO_PROCESADO:
                procesados += 1
            else:
                fallidos += 1
            print(f"[{indice:02d}/{len(archivos)}] {origen.name}: {resultado['detalle']}")
            time.sleep(argumentos.pausa)

        print(
            f"\nResumen: {procesados} procesados, {fallidos} con error, "
            f"{omitidos} omitidos por duplicado."
        )
        print(f"Administrador: {CORREO_DEMO} / {CLAVE_DEMO}")
        print(f"Usuario:       {CORREO_USUARIO} / {CLAVE_USUARIO}")
        print("Aplicación en http://localhost:5000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
