# Plan de implementación

1. Instalar Python 3.10+.
2. Crear el entorno virtual e instalar `0.3 Desarrollo/requirements.txt`.
3. Copiar `.env.example` a `.env` y cambiar la clave de sesión.
4. Ejecutar `flask --app app init-db` desde `0.3 Desarrollo`.
5. Iniciar con `flask --app app run --debug`.
6. Crear la primera cuenta; queda como administrador.
7. Crear un repositorio, cargar documentos de `11_repositorio_pruebas` y revisar búsqueda/descarga.

Para una instalación futura se reemplaza el servidor de desarrollo por un servidor WSGI y se configura HTTPS.

