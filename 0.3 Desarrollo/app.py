"""Sistema Inteligente de Gestión y Análisis Documental.

Aplicación Flask que gestiona repositorios de documentos y aplica inteligencia
artificial (Google Gemini) para clasificarlos, resumirlos, extraer sus datos
clave, buscarlos por contenido y responder preguntas en lenguaje natural.

Flujo implementado:
    archivo -> extracción de texto -> análisis IA -> almacenamiento
    -> búsqueda léxica o semántica -> respuesta con fuentes citadas
"""

from __future__ import annotations

import json
import os
import sqlite3
from functools import wraps
from pathlib import Path
from uuid import uuid4

import click
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from services import ai_service, extractor, procesamiento, rag
from services.ai_service import ErrorIA

BASE_DIR = Path(__file__).resolve().parent
CATEGORIAS = ai_service.CATEGORIAS

# Formatos admitidos y su descripción para los formularios.
FORMATOS_PERMITIDOS = extractor.FORMATOS
ACEPTA_HTML = ",".join(sorted(FORMATOS_PERMITIDOS))

# Columnas añadidas después de la primera versión del esquema. Se agregan a
# bases de datos ya creadas sin perder los registros existentes.
COLUMNAS_NUEVAS = {
    "error_procesamiento": "TEXT",
    "palabras_clave": "TEXT",
    "datos_extraidos": "TEXT",
    "modelo_ia": "TEXT",
    "procesado_en": "TIMESTAMP",
}

load_dotenv(BASE_DIR / ".env")


def create_app(test_config: dict | None = None) -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(
        __name__,
        instance_path=str(BASE_DIR / "instance"),
        instance_relative_config=True,
    )
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "solo-desarrollo-cambie-esta-clave"),
        DATABASE=os.getenv(
            "DATABASE_PATH", str(Path(app.instance_path) / "gestion_documental.sqlite3")
        ),
        UPLOAD_FOLDER=os.getenv(
            "UPLOAD_FOLDER", str(Path(app.instance_path) / "uploads")
        ),
        # Tamaño total de la petición: permite subir muchos archivos de una vez.
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 500 * 1024 * 1024)),
        # Tamaño máximo por archivo, que es el límite que se valida y comunica.
        MAX_FILE_SIZE=int(os.getenv("MAX_FILE_SIZE", 25 * 1024 * 1024)),
        # Con varios archivos el análisis corre en segundo plano; las pruebas
        # lo desactivan para obtener resultados deterministas.
        PROCESAR_EN_SEGUNDO_PLANO=os.getenv("PROCESAR_EN_SEGUNDO_PLANO", "1") == "1",
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    app.teardown_appcontext(cerrar_db)
    app.cli.add_command(init_db_command)

    with app.app_context():
        init_db()

    registrar_rutas(app)
    registrar_errores(app)
    return app


def get_db() -> sqlite3.Connection:
    """Obtiene una conexión SQLite por cada contexto de solicitud."""
    if "db" not in g:
        # Las marcas de tiempo se leen como texto ISO tal como las guarda
        # SQLite; no se usan conversores automáticos (obsoletos en Python 3.12).
        g.db = sqlite3.connect(current_app_config("DATABASE"))
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def current_app_config(key: str):
    """Evita importar la instancia global de Flask en las funciones de datos."""
    from flask import current_app

    return current_app.config[key]


def cerrar_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Crea las tablas que aún no existan y aplica las migraciones menores."""
    db = get_db()
    esquema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db.executescript(esquema)

    existentes = {fila["name"] for fila in db.execute("PRAGMA table_info(documentos)")}
    for columna, tipo in COLUMNAS_NUEVAS.items():
        if columna not in existentes:
            db.execute(f"ALTER TABLE documentos ADD COLUMN {columna} {tipo}")
    db.commit()


@click.command("init-db")
def init_db_command() -> None:
    """Inicializa la base de datos desde la terminal."""
    init_db()
    click.echo("Base de datos inicializada.")


def login_required(view):
    """Protege las vistas que requieren una sesión iniciada."""

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.usuario is None:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def extension_permitida(nombre: str) -> bool:
    return extractor.formato_admitido(nombre)


def guardar_documentos(repositorio_id: int, archivos: list) -> dict:
    """Guarda en disco y registra todos los archivos válidos de una carga.

    Devuelve los identificadores guardados y la lista de rechazos con su causa,
    de modo que un archivo inválido no cancele el resto del lote.
    """
    db = get_db()
    carpeta = Path(current_app_config("UPLOAD_FOLDER"))
    maximo = current_app_config("MAX_FILE_SIZE")
    guardados: list[int] = []
    rechazados: list[str] = []

    for archivo in archivos:
        if archivo is None or not archivo.filename:
            continue
        if not extension_permitida(archivo.filename):
            rechazados.append(f"{archivo.filename}: formato no admitido")
            registrar_actividad(
                "CARGA_RECHAZADA", f"Formato no admitido: {archivo.filename}", nivel="ERROR"
            )
            continue

        nombre_original = secure_filename(archivo.filename) or "documento"
        extension = Path(nombre_original).suffix.lower()
        nombre_almacenado = f"{uuid4().hex}{extension}"
        ruta = carpeta / nombre_almacenado
        archivo.save(ruta)
        tamano = ruta.stat().st_size

        if tamano > maximo:
            ruta.unlink(missing_ok=True)
            rechazados.append(
                f"{nombre_original}: supera los {maximo // (1024 * 1024)} MB por archivo"
            )
            registrar_actividad(
                "CARGA_RECHAZADA", f"Archivo demasiado grande: {nombre_original}", nivel="ERROR"
            )
            continue

        try:
            cursor = db.execute(
                """
                INSERT INTO documentos (
                    repositorio_id, titulo, descripcion, categoria,
                    nombre_original, nombre_almacenado, tipo_mime, tamano_bytes,
                    estado_procesamiento, creado_por
                ) VALUES (?, ?, ?, 'Otro', ?, ?, ?, ?, ?, ?)
                """,
                (
                    repositorio_id,
                    Path(nombre_original).stem,
                    "",
                    nombre_original,
                    nombre_almacenado,
                    archivo.mimetype or "application/octet-stream",
                    tamano,
                    procesamiento.ESTADO_PENDIENTE,
                    g.usuario["id"],
                ),
            )
        except Exception:
            ruta.unlink(missing_ok=True)
            raise

        guardados.append(cursor.lastrowid)
        registrar_actividad("CARGAR_DOCUMENTO", f"Documento cargado: {nombre_original}")

    db.commit()
    return {"guardados": guardados, "rechazados": rechazados}


def lanzar_procesamiento(ids: list[int]) -> str:
    """Procesa los documentos recién cargados y describe lo ocurrido.

    Con un solo archivo el análisis es inmediato, para que el usuario vea el
    resultado enseguida. Con varios se delega a un trabajador en segundo plano,
    de modo que la cantidad de archivos no bloquee la página.
    """
    if not ids:
        return ""

    db = get_db()
    en_segundo_plano = current_app_config("PROCESAR_EN_SEGUNDO_PLANO")

    if len(ids) == 1 or not en_segundo_plano:
        procesados = fallidos = 0
        carpeta = Path(current_app_config("UPLOAD_FOLDER"))
        for documento_id in ids:
            fila = db.execute(
                "SELECT nombre_original, nombre_almacenado FROM documentos WHERE id = ?",
                (documento_id,),
            ).fetchone()
            resultado = procesamiento.procesar_documento(
                db, documento_id, carpeta / fila["nombre_almacenado"]
            )
            registrar_actividad(
                "PROCESAR_DOCUMENTO",
                f"{fila['nombre_original']}: {resultado['detalle']}",
                nivel=(
                    "INFO"
                    if resultado["estado"] == procesamiento.ESTADO_PROCESADO
                    else "ERROR"
                ),
            )
            if resultado["estado"] == procesamiento.ESTADO_PROCESADO:
                procesados += 1
            else:
                fallidos += 1
        db.commit()
        if len(ids) == 1:
            return resultado["detalle"]
        return f"{procesados} documento(s) analizados y {fallidos} con error."

    procesamiento.iniciar_trabajador(
        current_app_config("DATABASE"), current_app_config("UPLOAD_FOLDER")
    )
    return (
        f"{len(ids)} documentos en cola. El análisis avanza en segundo plano: "
        "actualiza la página para ver cómo pasan a Procesado."
    )


def registrar_actividad(accion: str, detalle: str, nivel: str = "INFO") -> None:
    """Guarda un evento en la bitácora (RF-15: errores y operaciones)."""
    db = get_db()
    db.execute(
        "INSERT INTO bitacora (usuario_id, accion, detalle, nivel) VALUES (?, ?, ?, ?)",
        (g.usuario["id"] if g.get("usuario") else None, accion, detalle[:500], nivel),
    )


def obtener_repositorio(repositorio_id: int) -> sqlite3.Row:
    repositorio = get_db().execute(
        """
        SELECT r.*, u.nombre AS propietario
        FROM repositorios r
        JOIN usuarios u ON u.id = r.propietario_id
        WHERE r.id = ?
        """,
        (repositorio_id,),
    ).fetchone()
    if repositorio is None:
        abort(404)
    if g.usuario["rol"] != "administrador" and repositorio["propietario_id"] != g.usuario["id"]:
        abort(403)
    return repositorio


def obtener_documento(documento_id: int) -> sqlite3.Row:
    documento = get_db().execute(
        """
        SELECT d.*, r.nombre AS repositorio_nombre, r.propietario_id
        FROM documentos d
        JOIN repositorios r ON r.id = d.repositorio_id
        WHERE d.id = ?
        """,
        (documento_id,),
    ).fetchone()
    if documento is None:
        abort(404)
    if g.usuario["rol"] != "administrador" and documento["propietario_id"] != g.usuario["id"]:
        abort(403)
    return documento


def datos_de(documento: sqlite3.Row) -> list[dict]:
    """Convierte el JSON de datos extraídos en una lista para la plantilla."""
    try:
        return json.loads(documento["datos_extraidos"] or "[]")
    except (json.JSONDecodeError, IndexError, KeyError):
        return []


def registrar_rutas(app: Flask) -> None:
    @app.before_request
    def cargar_usuario_actual() -> None:
        usuario_id = session.get("usuario_id")
        g.usuario = (
            None
            if usuario_id is None
            else get_db()
            .execute(
                "SELECT id, nombre, correo, rol FROM usuarios WHERE id = ?", (usuario_id,)
            )
            .fetchone()
        )

    @app.route("/")
    def inicio():
        return redirect(url_for("dashboard" if g.usuario else "login"))

    # ------------------------------------------------------------------
    # Autenticación
    # ------------------------------------------------------------------

    @app.route("/registro", methods=("GET", "POST"))
    def registro():
        if g.usuario:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            correo = request.form.get("correo", "").strip().lower()
            clave = request.form.get("clave", "")
            error = None
            if len(nombre) < 3:
                error = "El nombre debe tener al menos 3 caracteres."
            elif "@" not in correo:
                error = "Ingresa un correo válido."
            elif len(clave) < 6:
                error = "La contraseña debe tener al menos 6 caracteres."

            if error is None:
                db = get_db()
                total = db.execute("SELECT COUNT(*) AS total FROM usuarios").fetchone()["total"]
                rol = "administrador" if total == 0 else "usuario"
                try:
                    db.execute(
                        """
                        INSERT INTO usuarios (nombre, correo, clave_hash, rol)
                        VALUES (?, ?, ?, ?)
                        """,
                        (nombre, correo, generate_password_hash(clave), rol),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "Ya existe una cuenta con ese correo."
                else:
                    flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
                    return redirect(url_for("login"))
            flash(error, "danger")
        return render_template("registro.html")

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if g.usuario:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            correo = request.form.get("correo", "").strip().lower()
            clave = request.form.get("clave", "")
            usuario = get_db().execute(
                "SELECT * FROM usuarios WHERE correo = ?", (correo,)
            ).fetchone()
            if usuario is None or not check_password_hash(usuario["clave_hash"], clave):
                flash("Correo o contraseña incorrectos.", "danger")
            else:
                session.clear()
                session["usuario_id"] = usuario["id"]
                return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/logout", methods=("POST",))
    @login_required
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ------------------------------------------------------------------
    # Panel de indicadores
    # ------------------------------------------------------------------

    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        filtro, parametros = filtro_propietario("r")
        metricas = db.execute(
            f"""
            SELECT COUNT(DISTINCT r.id) AS repositorios,
                   COUNT(d.id) AS documentos,
                   COALESCE(SUM(d.tamano_bytes), 0) AS bytes_usados,
                   SUM(CASE WHEN d.estado_procesamiento = 'Procesado' THEN 1 ELSE 0 END) AS procesados,
                   SUM(CASE WHEN d.estado_procesamiento = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes,
                   SUM(CASE WHEN d.estado_procesamiento = 'Error' THEN 1 ELSE 0 END) AS con_error
            FROM repositorios r
            LEFT JOIN documentos d ON d.repositorio_id = r.id
            {filtro}
            """,
            parametros,
        ).fetchone()
        por_categoria = db.execute(
            f"""
            SELECT d.categoria, COUNT(*) AS total
            FROM documentos d
            JOIN repositorios r ON r.id = d.repositorio_id
            {filtro}
            GROUP BY d.categoria
            ORDER BY total DESC
            """,
            parametros,
        ).fetchall()
        recientes = db.execute(
            f"""
            SELECT d.id, d.titulo, d.categoria, d.estado_procesamiento,
                   r.id AS repositorio_id, d.creado_en,
                   r.nombre AS repositorio_nombre
            FROM documentos d
            JOIN repositorios r ON r.id = d.repositorio_id
            {filtro}
            ORDER BY d.creado_en DESC
            LIMIT 5
            """,
            parametros,
        ).fetchall()
        actividad = db.execute(
            """
            SELECT b.accion, b.detalle, b.nivel, b.creado_en, u.nombre
            FROM bitacora b
            LEFT JOIN usuarios u ON u.id = b.usuario_id
            ORDER BY b.creado_en DESC LIMIT 8
            """
        ).fetchall()
        consultas = db.execute(
            "SELECT COUNT(*) AS total FROM consultas_ia"
        ).fetchone()["total"]
        return render_template(
            "dashboard.html",
            metricas=metricas,
            por_categoria=por_categoria,
            recientes=recientes,
            actividad=actividad,
            consultas=consultas,
            estado_ia=ai_service.estado_integracion(),
        )

    # ------------------------------------------------------------------
    # Repositorios
    # ------------------------------------------------------------------

    @app.route("/repositorios")
    @login_required
    def repositorios():
        filtro, parametros = filtro_propietario("r")
        lista = get_db().execute(
            f"""
            SELECT r.*, u.nombre AS propietario, COUNT(d.id) AS total_documentos
            FROM repositorios r
            JOIN usuarios u ON u.id = r.propietario_id
            LEFT JOIN documentos d ON d.repositorio_id = r.id
            {filtro}
            GROUP BY r.id
            ORDER BY r.creado_en DESC
            """,
            parametros,
        ).fetchall()
        return render_template("repositorios.html", repositorios=lista)

    @app.route("/repositorios/nuevo", methods=("GET", "POST"))
    @login_required
    def nuevo_repositorio():
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            if not nombre:
                flash("El nombre del repositorio es obligatorio.", "danger")
            else:
                db = get_db()
                db.execute(
                    """
                    INSERT INTO repositorios (nombre, descripcion, propietario_id)
                    VALUES (?, ?, ?)
                    """,
                    (nombre, descripcion, g.usuario["id"]),
                )
                registrar_actividad("CREAR_REPOSITORIO", f"Repositorio creado: {nombre}")
                db.commit()
                flash("Repositorio creado correctamente.", "success")
                return redirect(url_for("repositorios"))
        return render_template("repositorio_form.html", repositorio=None)

    @app.route("/repositorios/<int:repositorio_id>")
    @login_required
    def detalle_repositorio(repositorio_id: int):
        repositorio = obtener_repositorio(repositorio_id)
        documentos = get_db().execute(
            """
            SELECT d.*, u.nombre AS autor
            FROM documentos d
            JOIN usuarios u ON u.id = d.creado_por
            WHERE d.repositorio_id = ?
            ORDER BY d.creado_en DESC
            """,
            (repositorio_id,),
        ).fetchall()
        return render_template(
            "repositorio_detalle.html",
            repositorio=repositorio,
            documentos=documentos,
            categorias=CATEGORIAS,
            acepta=ACEPTA_HTML,
            pendientes=procesamiento.contar_pendientes(get_db()),
        )

    @app.route("/repositorios/<int:repositorio_id>/editar", methods=("GET", "POST"))
    @login_required
    def editar_repositorio(repositorio_id: int):
        repositorio = obtener_repositorio(repositorio_id)
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            if not nombre:
                flash("El nombre es obligatorio.", "danger")
            else:
                db = get_db()
                db.execute(
                    """
                    UPDATE repositorios
                    SET nombre = ?, descripcion = ?, actualizado_en = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (nombre, descripcion, repositorio_id),
                )
                registrar_actividad("EDITAR_REPOSITORIO", f"Repositorio editado: {nombre}")
                db.commit()
                flash("Repositorio actualizado.", "success")
                return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))
        return render_template("repositorio_form.html", repositorio=repositorio)

    @app.route("/repositorios/<int:repositorio_id>/eliminar", methods=("POST",))
    @login_required
    def eliminar_repositorio(repositorio_id: int):
        repositorio = obtener_repositorio(repositorio_id)
        db = get_db()
        total = db.execute(
            "SELECT COUNT(*) AS total FROM documentos WHERE repositorio_id = ?",
            (repositorio_id,),
        ).fetchone()["total"]
        if total:
            flash("Elimina primero los documentos del repositorio.", "warning")
            return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))
        db.execute("DELETE FROM repositorios WHERE id = ?", (repositorio_id,))
        registrar_actividad(
            "ELIMINAR_REPOSITORIO", f"Repositorio eliminado: {repositorio['nombre']}"
        )
        db.commit()
        flash("Repositorio eliminado.", "success")
        return redirect(url_for("repositorios"))

    # ------------------------------------------------------------------
    # Documentos y procesamiento con IA
    # ------------------------------------------------------------------

    @app.route("/repositorios/<int:repositorio_id>/documentos", methods=("POST",))
    @login_required
    def subir_documento(repositorio_id: int):
        obtener_repositorio(repositorio_id)
        archivos = request.files.getlist("archivo")
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not any(a.filename for a in archivos):
            flash("Selecciona al menos un archivo.", "danger")
            return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))

        carga = guardar_documentos(repositorio_id, archivos)
        if not carga["guardados"]:
            flash(" · ".join(carga["rechazados"]) or "No se guardó ningún archivo.", "danger")
            return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))

        # Con un único archivo se respetan el título y la descripción escritos.
        if len(carga["guardados"]) == 1 and (titulo or descripcion):
            get_db().execute(
                """
                UPDATE documentos
                SET titulo = COALESCE(NULLIF(?, ''), titulo), descripcion = ?
                WHERE id = ?
                """,
                (titulo, descripcion, carga["guardados"][0]),
            )
            get_db().commit()

        detalle = lanzar_procesamiento(carga["guardados"])
        avisar_de_la_carga(carga, detalle)

        if len(carga["guardados"]) == 1:
            return redirect(url_for("detalle_documento", documento_id=carga["guardados"][0]))
        return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))

    @app.route("/asistente/documentos", methods=("POST",))
    @login_required
    def subir_desde_asistente():
        """Carga documentos a la base de conocimiento desde el propio asistente."""
        archivos = request.files.getlist("archivo")
        if not any(a.filename for a in archivos):
            flash("Selecciona al menos un archivo.", "danger")
            return redirect(url_for("asistente"))

        destino = request.form.get("repositorio_id", "").strip()
        if destino:
            repositorio_id = obtener_repositorio(int(destino))["id"]
        else:
            repositorio_id = repositorio_del_asistente()

        carga = guardar_documentos(repositorio_id, archivos)
        if not carga["guardados"]:
            flash(" · ".join(carga["rechazados"]) or "No se guardó ningún archivo.", "danger")
            return redirect(url_for("asistente"))

        detalle = lanzar_procesamiento(carga["guardados"])
        avisar_de_la_carga(carga, detalle)
        return redirect(url_for("asistente"))

    @app.route("/procesar-pendientes", methods=("POST",))
    @login_required
    def procesar_pendientes():
        """Reanuda el análisis de los documentos que quedaron en Pendiente."""
        if procesamiento.trabajador_activo():
            flash("El análisis ya está en curso. Actualiza la página en unos segundos.", "warning")
        elif procesamiento.contar_pendientes(get_db()) == 0:
            flash("No hay documentos pendientes.", "success")
        elif current_app_config("PROCESAR_EN_SEGUNDO_PLANO"):
            procesamiento.iniciar_trabajador(
                current_app_config("DATABASE"), current_app_config("UPLOAD_FOLDER")
            )
            flash("Análisis reanudado en segundo plano.", "success")
        else:
            resumen = procesamiento.procesar_pendientes(
                current_app_config("DATABASE"), current_app_config("UPLOAD_FOLDER")
            )
            flash(
                f"{resumen['procesados']} documento(s) analizados y "
                f"{resumen['fallidos']} con error.",
                "success",
            )
        return redirect(request.referrer or url_for("asistente"))

    def repositorio_del_asistente() -> int:
        """Devuelve el repositorio propio del usuario, creándolo si hace falta."""
        db = get_db()
        fila = db.execute(
            "SELECT id FROM repositorios WHERE propietario_id = ? ORDER BY id LIMIT 1",
            (g.usuario["id"],),
        ).fetchone()
        if fila is not None:
            return fila["id"]
        cursor = db.execute(
            """
            INSERT INTO repositorios (nombre, descripcion, propietario_id)
            VALUES (?, ?, ?)
            """,
            (
                "Documentos del asistente",
                "Repositorio creado automáticamente al cargar documentos desde el asistente.",
                g.usuario["id"],
            ),
        )
        registrar_actividad("CREAR_REPOSITORIO", "Repositorio del asistente creado")
        db.commit()
        return cursor.lastrowid

    def avisar_de_la_carga(carga: dict, detalle: str) -> None:
        """Muestra un mensaje único con lo cargado y lo rechazado."""
        total = len(carga["guardados"])
        flash(f"{total} documento(s) cargados. {detalle}".strip(), "success")
        if carga["rechazados"]:
            flash(
                f"{len(carga['rechazados'])} archivo(s) no se cargaron: "
                + " · ".join(carga["rechazados"][:5]),
                "warning",
            )

    @app.route("/documentos/<int:documento_id>")
    @login_required
    def detalle_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        fragmentos = get_db().execute(
            "SELECT COUNT(*) AS total FROM fragmentos WHERE documento_id = ?", (documento_id,)
        ).fetchone()["total"]
        return render_template(
            "documento_detalle.html",
            documento=documento,
            datos=datos_de(documento),
            fragmentos=fragmentos,
        )

    @app.route("/documentos/<int:documento_id>/procesar", methods=("POST",))
    @login_required
    def reprocesar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        db = get_db()
        ruta = Path(current_app_config("UPLOAD_FOLDER")) / documento["nombre_almacenado"]
        resultado = procesamiento.procesar_documento(db, documento_id, ruta)
        registrar_actividad(
            "REPROCESAR_DOCUMENTO",
            f"{documento['nombre_original']}: {resultado['detalle']}",
            nivel="INFO" if resultado["estado"] == procesamiento.ESTADO_PROCESADO else "ERROR",
        )
        db.commit()
        categoria = "success" if resultado["estado"] == procesamiento.ESTADO_PROCESADO else "danger"
        flash(resultado["detalle"], categoria)
        return redirect(url_for("detalle_documento", documento_id=documento_id))

    @app.route("/documentos/<int:documento_id>/descargar")
    @login_required
    def descargar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        ruta = Path(current_app_config("UPLOAD_FOLDER")) / documento["nombre_almacenado"]
        if not ruta.exists():
            db = get_db()
            registrar_actividad(
                "DESCARGA_FALLIDA",
                f"Archivo ausente en disco: {documento['nombre_original']}",
                nivel="ERROR",
            )
            db.commit()
            abort(404)
        registrar_actividad(
            "DESCARGAR_DOCUMENTO", f"Documento descargado: {documento['nombre_original']}"
        )
        get_db().commit()
        return send_from_directory(
            current_app_config("UPLOAD_FOLDER"),
            documento["nombre_almacenado"],
            as_attachment=True,
            download_name=documento["nombre_original"],
        )

    @app.route("/documentos/<int:documento_id>/editar", methods=("GET", "POST"))
    @login_required
    def editar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            categoria = request.form.get("categoria", "Otro")
            if not titulo:
                flash("El título es obligatorio.", "danger")
            elif categoria not in CATEGORIAS:
                flash("Selecciona una categoría válida.", "danger")
            else:
                db = get_db()
                db.execute(
                    """
                    UPDATE documentos
                    SET titulo = ?, descripcion = ?, categoria = ?,
                        actualizado_en = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (titulo, descripcion, categoria, documento_id),
                )
                registrar_actividad("EDITAR_DOCUMENTO", f"Documento editado: {titulo}")
                db.commit()
                flash("Documento actualizado.", "success")
                return redirect(url_for("detalle_documento", documento_id=documento_id))
        return render_template(
            "documento_form.html", documento=documento, categorias=CATEGORIAS
        )

    @app.route("/documentos/<int:documento_id>/eliminar", methods=("POST",))
    @login_required
    def eliminar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        db = get_db()
        db.execute("DELETE FROM fragmentos WHERE documento_id = ?", (documento_id,))
        db.execute("DELETE FROM documentos WHERE id = ?", (documento_id,))
        registrar_actividad(
            "ELIMINAR_DOCUMENTO", f"Documento eliminado: {documento['nombre_original']}"
        )
        db.commit()
        (Path(current_app_config("UPLOAD_FOLDER")) / documento["nombre_almacenado"]).unlink(
            missing_ok=True
        )
        flash("Documento eliminado.", "success")
        return redirect(
            url_for("detalle_repositorio", repositorio_id=documento["repositorio_id"])
        )

    # ------------------------------------------------------------------
    # Búsqueda: léxica sobre el contenido y semántica sobre los vectores
    # ------------------------------------------------------------------

    @app.route("/buscar")
    @login_required
    def buscar():
        termino = request.args.get("q", "").strip()
        modo = request.args.get("modo", "texto")
        resultados: list = []
        error = None

        if termino and modo == "semantica":
            try:
                resultados = buscar_semantico(termino)
            except ErrorIA as exc:
                error = str(exc)
                registrar_actividad("BUSQUEDA_SEMANTICA", error, nivel="ERROR")
                get_db().commit()
        elif termino:
            resultados = buscar_texto(termino)

        return render_template(
            "buscar.html", termino=termino, modo=modo, resultados=resultados, error=error
        )

    def buscar_texto(termino: str) -> list[dict]:
        """Busca dentro del contenido extraído y de los metadatos (RF-12)."""
        patron = f"%{termino}%"
        filtro, parametros = filtro_propietario("r")
        conector = "AND" if filtro else "WHERE"
        filas = get_db().execute(
            f"""
            SELECT d.id, d.titulo, d.categoria, d.resumen, d.nombre_original,
                   d.contenido_extraido, d.creado_en,
                   r.id AS repositorio_id, r.nombre AS repositorio_nombre
            FROM documentos d
            JOIN repositorios r ON r.id = d.repositorio_id
            {filtro}
            {conector} (d.titulo LIKE ? OR d.descripcion LIKE ?
                        OR d.nombre_original LIKE ? OR d.categoria LIKE ?
                        OR d.palabras_clave LIKE ? OR d.contenido_extraido LIKE ?)
            ORDER BY d.creado_en DESC
            LIMIT 50
            """,
            (*parametros, patron, patron, patron, patron, patron, patron),
        ).fetchall()
        return [
            {
                "id": f["id"],
                "titulo": f["titulo"],
                "categoria": f["categoria"],
                "repositorio_id": f["repositorio_id"],
                "repositorio_nombre": f["repositorio_nombre"],
                "extracto": extracto(f["contenido_extraido"], termino) or (f["resumen"] or ""),
                "similitud": None,
            }
            for f in filas
        ]

    def buscar_semantico(termino: str) -> list[dict]:
        """Busca por significado usando los vectores de los fragmentos (RF-IA-05)."""
        db = get_db()
        filtro, parametros = filtro_propietario("r")
        filas = db.execute(
            f"""
            SELECT f.documento_id, f.texto, f.vector, d.titulo, d.categoria,
                   r.id AS repositorio_id, r.nombre AS repositorio_nombre
            FROM fragmentos f
            JOIN documentos d ON d.id = f.documento_id
            JOIN repositorios r ON r.id = d.repositorio_id
            {filtro}
            """,
            parametros,
        ).fetchall()

        vistos: dict[int, dict] = {}
        for fragmento in rag.buscar_fragmentos(db, termino, filas, top_k=8):
            if fragmento["documento_id"] in vistos:
                continue
            fila = next(f for f in filas if f["documento_id"] == fragmento["documento_id"])
            vistos[fragmento["documento_id"]] = {
                "id": fragmento["documento_id"],
                "titulo": fila["titulo"],
                "categoria": fila["categoria"],
                "repositorio_id": fila["repositorio_id"],
                "repositorio_nombre": fila["repositorio_nombre"],
                "extracto": fragmento["texto"][:280],
                "similitud": round(fragmento["similitud"] * 100, 1),
            }
        return list(vistos.values())[:5]

    # ------------------------------------------------------------------
    # Asistente: preguntas en lenguaje natural sobre los documentos
    # ------------------------------------------------------------------

    @app.route("/asistente", methods=("GET", "POST"))
    @login_required
    def asistente():
        db = get_db()
        respuesta = None
        fuentes: list[dict] = []
        pregunta = ""
        error = None

        if request.method == "POST":
            pregunta = request.form.get("pregunta", "").strip()
            if len(pregunta) < 5:
                error = "Escribe una pregunta de al menos 5 caracteres."
            else:
                filtro, parametros = filtro_propietario("r")
                filas = db.execute(
                    f"""
                    SELECT f.documento_id, f.texto, f.vector, d.titulo
                    FROM fragmentos f
                    JOIN documentos d ON d.id = f.documento_id
                    JOIN repositorios r ON r.id = d.repositorio_id
                    {filtro}
                    """,
                    parametros,
                ).fetchall()
                if not filas:
                    error = (
                        "Todavía no hay documentos indexados. Carga documentos y "
                        "espera a que queden en estado Procesado."
                    )
                else:
                    try:
                        fuentes = rag.buscar_fragmentos(db, pregunta, filas)
                        respuesta = ai_service.responder_pregunta(pregunta, fuentes)
                        db.execute(
                            """
                            INSERT INTO consultas_ia (usuario_id, pregunta, respuesta, fuentes)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                g.usuario["id"],
                                pregunta,
                                respuesta,
                                ", ".join(sorted({f["titulo"] for f in fuentes})),
                            ),
                        )
                        registrar_actividad("CONSULTA_IA", f"Pregunta: {pregunta}")
                        db.commit()
                    except ErrorIA as exc:
                        error = str(exc)
                        registrar_actividad("CONSULTA_IA", error, nivel="ERROR")
                        db.commit()

        historial = db.execute(
            """
            SELECT pregunta, respuesta, fuentes, creado_en
            FROM consultas_ia
            WHERE usuario_id = ?
            ORDER BY creado_en DESC LIMIT 5
            """,
            (g.usuario["id"],),
        ).fetchall()

        filtro, parametros = filtro_propietario("r")
        repositorios_disponibles = db.execute(
            f"""
            SELECT r.id, r.nombre, COUNT(d.id) AS total_documentos
            FROM repositorios r
            LEFT JOIN documentos d ON d.repositorio_id = r.id
            {filtro}
            GROUP BY r.id
            ORDER BY r.nombre
            """,
            parametros,
        ).fetchall()

        return render_template(
            "asistente.html",
            pregunta=pregunta,
            respuesta=respuesta,
            fuentes=fuentes,
            error=error,
            historial=historial,
            estado=ai_service.estado_integracion(),
            repositorios=repositorios_disponibles,
            pendientes=procesamiento.contar_pendientes(db),
            indexados=db.execute(
                f"""
                SELECT COUNT(DISTINCT f.documento_id) AS total
                FROM fragmentos f
                JOIN documentos d ON d.id = f.documento_id
                JOIN repositorios r ON r.id = d.repositorio_id
                {filtro}
                """,
                parametros,
            ).fetchone()["total"],
            acepta=ACEPTA_HTML,
        )

    @app.route("/salud")
    def salud():
        """Verificación de disponibilidad del servicio (RF-17)."""
        return {
            "estado": "ok",
            "base_datos": "conectada" if get_db() else "sin conexión",
            "ia": ai_service.estado_integracion(),
        }

    def filtro_propietario(alias: str) -> tuple[str, tuple]:
        if g.usuario["rol"] == "administrador":
            return "", ()
        return f"WHERE {alias}.propietario_id = ?", (g.usuario["id"],)


def extracto(contenido: str | None, termino: str, ventana: int = 120) -> str:
    """Devuelve el fragmento de texto alrededor de la primera coincidencia."""
    if not contenido:
        return ""
    posicion = contenido.lower().find(termino.lower())
    if posicion < 0:
        return contenido[:200].strip()
    inicio = max(posicion - ventana, 0)
    fin = min(posicion + len(termino) + ventana, len(contenido))
    prefijo = "..." if inicio > 0 else ""
    sufijo = "..." if fin < len(contenido) else ""
    return f"{prefijo}{contenido[inicio:fin].strip()}{sufijo}"


def registrar_errores(app: Flask) -> None:
    @app.errorhandler(403)
    def prohibido(_error):
        return render_template(
            "error.html", codigo=403, mensaje="No tienes permiso para ver este recurso."
        ), 403

    @app.errorhandler(404)
    def no_encontrado(_error):
        return render_template(
            "error.html", codigo=404, mensaje="El recurso solicitado no existe."
        ), 404

    @app.errorhandler(413)
    def archivo_grande(_error):
        return render_template(
            "error.html", codigo=413, mensaje="El archivo supera el tamaño máximo permitido."
        ), 413

    @app.errorhandler(500)
    def error_interno(error):
        app.logger.exception("Error interno no controlado: %s", error)
        return render_template(
            "error.html",
            codigo=500,
            mensaje="Ocurrió un error interno. El detalle quedó en el registro del servidor.",
        ), 500


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
