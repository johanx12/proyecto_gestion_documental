# Modelo de datos

```text
usuarios 1 ─── N repositorios 1 ─── N documentos
usuarios 1 ─── N bitacora
```

## Entidades

- `usuarios`: identidad, correo único, hash de clave y rol.
- `repositorios`: agrupación propiedad de un usuario.
- `documentos`: título, categoría, nombre original, archivo almacenado, estado y fechas.
- `bitacora`: acción, detalle, usuario y fecha para seguimiento.

La tabla `documentos` ya reserva `resumen` y `contenido_extraido` para una futura iteración, pero no se rellenan mientras la IA permanezca pendiente.

