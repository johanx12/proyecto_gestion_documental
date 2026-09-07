# Diseño

El diseño usa una arquitectura web sencilla para que el proyecto sea fácil de ejecutar y extender.

## Capas

1. **Presentación:** plantillas Jinja, HTML semántico y CSS en `templates/` y `static/`.
2. **Aplicación:** rutas Flask en `app.py`, sesiones y validaciones.
3. **Persistencia:** SQLite mediante `schema.sql`.
4. **Archivos:** almacenamiento local fuera del código, con nombre interno UUID.
5. **Extensión IA:** `services/ai_service.py`, actualmente informativa y sin proveedor.

## Flujo principal

```text
Cliente -> login -> dashboard -> repositorio -> carga de documento
                                      |              |
                                      +-> búsqueda <- SQLite + almacenamiento
Administrador -> dashboard / bitácora / reporte mensual futuro
```

## Decisiones

- Flask reduce la configuración para una entrega universitaria.
- SQLite no necesita servidor adicional.
- Las contraseñas se almacenan con hash de Werkzeug.
- El documento binario se guarda separado de los metadatos.
- Las consultas filtran por propietario para evitar acceso cruzado.
- IA queda con estado `Pendiente de implementación` y no se incluye SDK.

