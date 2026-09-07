# Desarrollo

Prototipo Flask para gestión de documentos. Se mantiene deliberadamente sencillo para que el equipo pueda leerlo y mejorarlo.

## Requisitos

- Python 3.10 o superior.
- No requiere servidor de base de datos ni proveedor de IA.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app app init-db
flask --app app run --debug
```

Abre `http://127.0.0.1:5000`, crea la primera cuenta y prueba el flujo. La primera cuenta recibe el rol `administrador`; las siguientes reciben `usuario`.

## Archivos locales

La base y las cargas se crean en `instance/`, carpeta excluida por `.gitignore`. Ajusta `DATABASE_PATH`, `UPLOAD_FOLDER` y `SECRET_KEY` mediante variables de entorno.

## Estado de IA

No hay SDK, llamada HTTP, modelo ni clave. La ruta `/ia` muestra el estado pendiente y `services/ai_service.py` contiene únicamente un contrato informativo.

