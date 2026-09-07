CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    clave_hash TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'usuario'
        CHECK (rol IN ('administrador', 'usuario')),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repositorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    propietario_id INTEGER NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (propietario_id) REFERENCES usuarios (id)
);

CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repositorio_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    categoria TEXT NOT NULL DEFAULT 'Otro',
    nombre_original TEXT NOT NULL,
    nombre_almacenado TEXT NOT NULL UNIQUE,
    tipo_mime TEXT NOT NULL,
    tamano_bytes INTEGER NOT NULL DEFAULT 0,
    estado_procesamiento TEXT NOT NULL DEFAULT 'Pendiente de implementación (IA)',
    resumen TEXT,
    contenido_extraido TEXT,
    creado_por INTEGER NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repositorio_id) REFERENCES repositorios (id),
    FOREIGN KEY (creado_por) REFERENCES usuarios (id)
);

CREATE TABLE IF NOT EXISTS bitacora (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    accion TEXT NOT NULL,
    detalle TEXT NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_documentos_repositorio
    ON documentos (repositorio_id);
CREATE INDEX IF NOT EXISTS idx_documentos_titulo
    ON documentos (titulo);
CREATE INDEX IF NOT EXISTS idx_bitacora_fecha
    ON bitacora (creado_en);
