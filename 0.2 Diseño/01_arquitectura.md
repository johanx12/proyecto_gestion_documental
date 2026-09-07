# Arquitectura y componentes

## Componentes

| Componente | Responsabilidad |
|---|---|
| `app.py` | Fábrica Flask, rutas, autenticación y validaciones. |
| `schema.sql` | Tablas, restricciones e índices. |
| `services/ai_service.py` | Contrato visible para una integración futura; no procesa. |
| `templates/` | Pantallas de login, tablero, repositorios y errores. |
| `static/` | Estilos de la interfaz. |
| `instance/` | Base de datos y archivos locales en ejecución; está ignorada por Git. |

## Seguridad básica

- La sesión guarda solamente el identificador del usuario.
- Las contraseñas usan `generate_password_hash` y `check_password_hash`.
- Se valida la extensión permitida y se usa `secure_filename`.
- Las rutas de repositorio y documento verifican propietario o rol de administrador.
- Los secretos se suministran mediante variables de entorno y nunca se suben.

