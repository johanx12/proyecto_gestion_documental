"""Aplicación académica de gestión documental.

Incluye autenticación básica, repositorios, carga de documentos y búsqueda por
metadatos. La integración de inteligencia artificial queda intencionalmente
pendiente por decisión del alcance actual del proyecto.
"""

from __future__ import annotations

import os
import sqlite3
from functools import wraps
from pathlib import Path
from uuid import uuid4

import click
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

from services.ai_service import estado_integracion


BASE_DIR = Path(__file__).resolve().parent
EXTENSIONES_PERMITIDAS = {"pdf", "docx", "txt"}
CATEGORIAS = ("Contrato", "Factura", "Informe", "Otro")


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
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)),
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
        g.db = sqlite3.connect(
            current_app_config("DATABASE"), detect_types=sqlite3.PARSE_DECLTYPES
        )
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
    """Crea las tablas que aún no existan sin borrar información previa."""
    db = get_db()
    esquema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db.executescript(esquema)
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
    return "." in nombre and nombre.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def registrar_actividad(accion: str, detalle: str) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO bitacora (usuario_id, accion, detalle) VALUES (?, ?, ?)",
        (g.usuario["id"] if g.usuario else None, accion, detalle),
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

    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()
        filtro, parametros = filtro_propietario("r")
        metricas = db.execute(
            f"""
            SELECT COUNT(DISTINCT r.id) AS repositorios,
                   COUNT(d.id) AS documentos,
                   COALESCE(SUM(d.tamano_bytes), 0) AS bytes_usados
            FROM repositorios r
            LEFT JOIN documentos d ON d.repositorio_id = r.id
            {filtro}
            """,
            parametros,
        ).fetchone()
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
            SELECT b.accion, b.detalle, b.creado_en, u.nombre
            FROM bitacora b
            LEFT JOIN usuarios u ON u.id = b.usuario_id
            ORDER BY b.creado_en DESC LIMIT 5
            """
        ).fetchall()
        return render_template(
            "dashboard.html", metricas=metricas, recientes=recientes, actividad=actividad
        )

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

    @app.route("/repositorios/<int:repositorio_id>/documentos", methods=("POST",))
    @login_required
    def subir_documento(repositorio_id: int):
        repositorio = obtener_repositorio(repositorio_id)
        archivo = request.files.get("archivo")
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria", "Otro")

        if archivo is None or not archivo.filename:
            flash("Selecciona un archivo.", "danger")
            return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))
        if not extension_permitida(archivo.filename):
            flash("Formato no permitido. Usa PDF, DOCX o TXT.", "danger")
            return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))
        if categoria not in CATEGORIAS:
            categoria = "Otro"

        nombre_original = secure_filename(archivo.filename)
        extension = Path(nombre_original).suffix.lower()
        nombre_almacenado = f"{uuid4().hex}{extension}"
        ruta = Path(current_app_config("UPLOAD_FOLDER")) / nombre_almacenado
        archivo.save(ruta)
        tamano = ruta.stat().st_size
        titulo = titulo or Path(nombre_original).stem

        db = get_db()
        try:
            db.execute(
                """
                INSERT INTO documentos (
                    repositorio_id, titulo, descripcion, categoria,
                    nombre_original, nombre_almacenado, tipo_mime, tamano_bytes,
                    estado_procesamiento, creado_por
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    repositorio_id,
                    titulo,
                    descripcion,
                    categoria,
                    nombre_original,
                    nombre_almacenado,
                    archivo.mimetype or "application/octet-stream",
                    tamano,
                    "Pendiente de implementación (IA)",
                    g.usuario["id"],
                ),
            )
            registrar_actividad(
                "CARGAR_DOCUMENTO",
                f"Documento {nombre_original} cargado en {repositorio['nombre']}",
            )
            db.commit()
        except Exception:
            ruta.unlink(missing_ok=True)
            raise

        flash("Documento cargado. El procesamiento con IA está pendiente.", "success")
        return redirect(url_for("detalle_repositorio", repositorio_id=repositorio_id))

    @app.route("/documentos/<int:documento_id>/descargar")
    @login_required
    def descargar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
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
                return redirect(
                    url_for("detalle_repositorio", repositorio_id=documento["repositorio_id"])
                )
        return render_template(
            "documento_form.html", documento=documento, categorias=CATEGORIAS
        )

    @app.route("/documentos/<int:documento_id>/eliminar", methods=("POST",))
    @login_required
    def eliminar_documento(documento_id: int):
        documento = obtener_documento(documento_id)
        db = get_db()
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

    @app.route("/buscar")
    @login_required
    def buscar():
        termino = request.args.get("q", "").strip()
        resultados = []
        if termino:
            patron = f"%{termino}%"
            filtro, parametros = filtro_propietario("r")
            conector = "AND" if filtro else "WHERE"
            resultados = get_db().execute(
                f"""
                SELECT d.id, d.titulo, d.descripcion, d.categoria, d.nombre_original,
                       d.creado_en, r.id AS repositorio_id, r.nombre AS repositorio_nombre
                FROM documentos d
                JOIN repositorios r ON r.id = d.repositorio_id
                {filtro}
                {conector} (d.titulo LIKE ? OR d.descripcion LIKE ?
                            OR d.nombre_original LIKE ? OR d.categoria LIKE ?)
                ORDER BY d.creado_en DESC
                LIMIT 50
                """,
                (*parametros, patron, patron, patron, patron),
            ).fetchall()
        return render_template("buscar.html", termino=termino, resultados=resultados)

    @app.route("/ia")
    @login_required
    def ia_pendiente():
        return render_template("ia_pendiente.html", estado=estado_integracion())

    def filtro_propietario(alias: str) -> tuple[str, tuple]:
        if g.usuario["rol"] == "administrador":
            return "", ()
        return f"WHERE {alias}.propietario_id = ?", (g.usuario["id"],)


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


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
