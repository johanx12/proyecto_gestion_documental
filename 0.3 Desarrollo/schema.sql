-- Esquema de la base de datos SQLite del sistema de gestión documental.
-- Se ejecuta en cada arranque con CREATE TABLE IF NOT EXISTS: crea lo que
-- falte y nunca borra información existente.

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

-- Un documento guarda tres capas: el archivo físico, el texto extraído y el
-- resultado del análisis de IA (categoría, resumen, palabras clave y datos).
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
    estado_procesamiento TEXT NOT NULL DEFAULT 'Pendiente',
    error_procesamiento TEXT,
    resumen TEXT,
    palabras_clave TEXT,
    datos_extraidos TEXT,
    contenido_extraido TEXT,
    modelo_ia TEXT,
    procesado_en TIMESTAMP,
    creado_por INTEGER NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repositorio_id) REFERENCES repositorios (id),
    FOREIGN KEY (creado_por) REFERENCES usuarios (id)
);

-- Índice semántico: un registro por fragmento de texto con su vector en JSON.
CREATE TABLE IF NOT EXISTS fragmentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER NOT NULL,
    orden INTEGER NOT NULL DEFAULT 0,
    texto TEXT NOT NULL,
    vector TEXT NOT NULL,
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (documento_id) REFERENCES documentos (id) ON DELETE CASCADE
);

-- Historial de preguntas en lenguaje natural con los documentos citados.
CREATE TABLE IF NOT EXISTS consultas_ia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fuentes TEXT NOT NULL DEFAULT '',
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bitacora (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    accion TEXT NOT NULL,
    detalle TEXT NOT NULL,
    nivel TEXT NOT NULL DEFAULT 'INFO' CHECK (nivel IN ('INFO', 'ERROR')),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_documentos_repositorio
    ON documentos (repositorio_id);
CREATE INDEX IF NOT EXISTS idx_documentos_titulo
    ON documentos (titulo);
CREATE INDEX IF NOT EXISTS idx_documentos_categoria
    ON documentos (categoria);
CREATE INDEX IF NOT EXISTS idx_fragmentos_documento
    ON fragmentos (documento_id);
CREATE INDEX IF NOT EXISTS idx_bitacora_fecha
    ON bitacora (creado_en);
