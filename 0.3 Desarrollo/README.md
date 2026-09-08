# 03 — Documento técnico de desarrollo

Aplicación web del Sistema Inteligente de Gestión y Análisis Documental.

## 1. Entorno de desarrollo

| Elemento | Valor |
|---|---|
| Lenguaje | Python 3.12 o superior (probado en 3.14) |
| Framework web | Flask 3 con plantillas Jinja2 |
| Base de datos | SQLite (archivo local, sin servidor) |
| Extracción | `pypdf` (PDF), `python-docx` (DOCX), `zipfile` + `ElementTree` (XLSX, PPTX, ODT) y lectores propios para texto, HTML y RTF |
| IA | API de Google Gemini vía `requests` |
| Pruebas | `pytest` |
| Sistema operativo de desarrollo | Windows 11; el proyecto también corre en Linux y macOS |

## 2. Configuración del proyecto

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux o macOS: source .venv/bin/activate
pip install -r "0.3 Desarrollo/requirements.txt"
```

Copia `.env.example` como `.env` dentro de `0.3 Desarrollo` y completa la clave:

```ini
SECRET_KEY=una-clave-aleatoria
GEMINI_API_KEY=tu-clave-de-google-ai-studio
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_EMBEDDING_DIM=768
```

Ejecución:

```bash
cd "0.3 Desarrollo"
python app.py
```

La aplicación queda en <http://localhost:5000>.

## 3. Estructura del código fuente

```text
0.3 Desarrollo/
├── app.py                  Fábrica Flask, rutas, permisos y manejo de errores
├── schema.sql              Tablas, restricciones e índices
├── requirements.txt        Dependencias de ejecución y pruebas
├── .env.example            Plantilla de configuración (sin credenciales)
├── services/
│   ├── extractor.py        Cualquier formato admitido -> texto; fragmentación
│   ├── ai_service.py       Llamadas a Gemini: análisis, embeddings, respuestas
│   ├── procesamiento.py    Orquestación del flujo y manejo de estados
│   └── rag.py              Recuperación semántica por similitud coseno
├── scripts/
│   ├── generar_documentos_prueba.py   Corpus de 30 documentos en 3 formatos
│   └── cargar_demo.py                 Carga y procesa el corpus completo
├── templates/              Pantallas HTML
├── static/styles.css       Estilos
├── tests/                  Pruebas automatizadas
└── instance/               Base de datos y archivos cargados (ignorado por Git)
```

## 4. Implementación del backend

`app.py` usa el patrón de fábrica (`create_app`). Cada solicitud abre una
conexión SQLite en `g`, que se cierra al terminar. `before_request` carga el
usuario de la sesión y el decorador `login_required` protege las vistas
privadas. La función `filtro_propietario` añade el filtro por dueño a todas las
consultas cuando el usuario no es administrador.

## 5. Implementación del frontend

Plantillas Jinja2 con herencia desde `base.html` y una hoja de estilos propia,
sin dependencias de terceros. Las pantallas son: acceso, registro, panel,
listado y ficha de repositorio, ficha de documento, búsqueda, asistente y error.

## 6. Base de datos y almacenamiento

El esquema se aplica en cada arranque con `CREATE TABLE IF NOT EXISTS`, y las
columnas añadidas después de la primera versión se agregan con `ALTER TABLE` si
faltan, de modo que una base existente se actualiza sin perder datos. Los
archivos se guardan en `instance/uploads` con un nombre UUID; el nombre original
se conserva solo como metadato.

## 7. Procesamiento de documentos

`services/extractor.py` convierte el archivo a texto según su formato: `pypdf`
para PDF, `python-docx` para DOCX, lectura del XML del contenedor ZIP para XLSX,
PPTX y ODT, limpieza de etiquetas para HTML y RTF, y lectura directa para los
formatos de texto. Un `.doc` antiguo se resuelve por su firma: si en realidad es
un DOCX renombrado se procesa como tal, y si es OLE2 se recupera el texto
legible del binario.

Si el resultado tiene menos de 20 caracteres se considera ilegible. En ese caso,
si el formato lo permite (PDF o imagen), `procesamiento.py` envía el archivo al
modelo multimodal para transcribirlo (OCR). Solo se marca `Error` cuando también
esa vía falla.

## 8. Integración de IA

`services/ai_service.py` es el único módulo que habla con el proveedor:

1. **Clasificación, resumen y extracción**: una llamada a `generateContent` con
   `responseSchema`, que obliga al modelo a devolver exactamente `categoria`,
   `resumen`, `palabras_clave` y `datos_extraidos`.
2. **Embeddings**: `embedContent` con `gemini-embedding-001` a 768 dimensiones,
   diferenciando `RETRIEVAL_DOCUMENT` (indexación) de `RETRIEVAL_QUERY` (consulta).
3. **Respuesta del asistente**: los fragmentos recuperados se envían como
   contexto con la instrucción de citar fuentes y de admitir cuando la
   información no está en el repositorio.
4. **Transcripción (OCR)**: el archivo se envía en `inline_data` junto a la
   instrucción de transcribirlo, para los PDF sin capa de texto y las imágenes.

Hay reintentos con espera creciente ante `429`, `500` y `503`; los demás
códigos abortan de inmediato y el detalle queda registrado.

## 9. Búsqueda y consulta

- **Léxica**: `LIKE` sobre título, descripción, nombre de archivo, categoría,
  palabras clave y **contenido extraído**, con extracto alrededor de la
  coincidencia.
- **Semántica**: se calcula el vector de la consulta y se ordena por similitud
  coseno contra los fragmentos que el usuario puede ver.
- **Asistente**: recupera los cinco fragmentos más cercanos y genera la
  respuesta citando los documentos.

## 10. Gestión de errores y validaciones

| Situación | Comportamiento |
|---|---|
| Extensión no permitida | Se rechaza antes de guardar y se registra en la bitácora con nivel `ERROR`. |
| Archivo mayor al máximo | Se descarta ese archivo con su causa; el resto del lote continúa. |
| Archivo sin texto legible | El documento queda en estado `Error` con el detalle. |
| Falla de la API de IA | Se conserva el texto extraído, el estado pasa a `Error` y el documento se puede reprocesar. |
| Recurso inexistente o ajeno | 404 y 403 con página propia. |
| Excepción no controlada | 500 con página propia; la traza queda en el log del servidor. |

## 11. Seguridad de credenciales

La clave vive en `.env`, que está en `.gitignore`. El repositorio solo publica
`.env.example` sin valores. La aplicación nunca imprime la clave y falla con un
mensaje claro cuando no está configurada.

## 12. Control de versiones

Git, con confirmaciones por fase del ciclo de desarrollo. Los directorios
`instance/`, `.venv/` y los archivos `.env` están excluidos.

## 13. Ejecución de las pruebas

```bash
cd "0.3 Desarrollo"
python -m pytest tests -v                       # 38 pruebas con dobles de IA
$env:PRUEBA_IA_REAL=1; python -m pytest tests/test_integracion_gemini.py -v   # 3 pruebas reales
```

## 14. Carga del repositorio de demostración

```bash
python scripts/generar_documentos_prueba.py   # opcional: regenera los 30 archivos
python scripts/cargar_demo.py                 # carga y procesa los 30 documentos
```

Deja creada la cuenta `admin@demo.com` / `admin123` y el repositorio
«Archivo corporativo» con todo el corpus procesado.
