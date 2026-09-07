# Manual técnico

Desde `0.3 Desarrollo`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

Para ejecutar las pruebas básicas, ubícate en la carpeta de desarrollo y ejecuta `pytest ../0.4 Pruebas` si se agregan casos automatizados. La base se crea desde `schema.sql`. La carpeta `instance/` contiene datos locales y está excluida de Git.

