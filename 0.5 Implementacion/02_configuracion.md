# Configuración rápida

Variables disponibles:

| Variable | Ejemplo | Uso |
|---|---|---|
| `SECRET_KEY` | `clave-local-larga` | Firmar sesiones. |
| `DATABASE_PATH` | `instance/gestion_documental.sqlite3` | Ruta de SQLite. |
| `UPLOAD_FOLDER` | `instance/uploads` | Archivos cargados. |
| `MAX_CONTENT_LENGTH` | `10485760` | Límite de 10 MB. |

No se necesita `OPENAI_API_KEY` en esta versión: la IA se encuentra pendiente y el código no realiza llamadas.

