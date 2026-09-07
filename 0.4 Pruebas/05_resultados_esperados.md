# Resultados esperados y registro de ejecución

## Advertencia de estado

Esta versión del documento es una **línea base de resultados esperados**. No constituye evidencia de ejecución. Todos los casos deben permanecer como `No ejecutado` hasta que una persona inicie el sistema, siga los pasos y adjunte evidencia verificable.

## Resumen esperado

| Caso | Resultado esperado resumido | Estado actual | Evidencia |
|---|---|---|---|
| CP-01 | Acceso al tablero del rol | No ejecutado | Pendiente |
| CP-02 | Rechazo seguro de contraseña errónea | No ejecutado | Pendiente |
| CP-03 | Sesión cerrada y rutas protegidas | No ejecutado | Pendiente |
| CP-04 | Función administrativa bloqueada | No ejecutado | Pendiente |
| CP-05 | Registro y archivo creados de forma coherente | No ejecutado | Pendiente |
| CP-06 | Formulario rechazado sin residuos | No ejecutado | Pendiente |
| CP-07 | Extensión peligrosa rechazada | No ejecutado | Pendiente |
| CP-08 | Resultados coinciden con texto y categoría | No ejecutado | Pendiente |
| CP-09 | Mensaje de lista vacía sin error | No ejecutado | Pendiente |
| CP-10 | Descarga correcta para usuario autorizado | No ejecutado | Pendiente |
| CP-11 | Descarga privada bloqueada | No ejecutado | Pendiente |
| CP-12 | Metadatos actualizados sin perder archivo | No ejecutado | Pendiente |
| CP-13 | Estado cambia y puede restaurarse | No ejecutado | Pendiente |
| CP-14 | Totales administrativos coherentes | No ejecutado | Pendiente |
| CP-15 | No existen llamadas a IA | Pendiente por alcance | Revisión futura |

## Plantilla por ejecución

Copiar este bloque por cada caso realmente evaluado:

```text
ID de ejecución:
Caso de prueba:
Versión o commit:
Fecha y hora:
Responsable:
Sistema operativo y navegador:
Datos utilizados:
Resultado obtenido:
Estado: Aprobado | Fallido | Bloqueado
Evidencia:
Defecto relacionado:
Observaciones:
```

## Reglas para decidir el estado

- Aprobado: el resultado observado coincide completamente con el esperado.
- Fallido: hay una diferencia reproducible entre ambos resultados.
- Bloqueado: una condición externa o un defecto previo impide terminar el caso.
- No ejecutado: todavía no existe observación ni evidencia.

Una captura de pantalla aislada no demuestra por sí sola la integridad de la base de datos o del archivo. Para CP-05, CP-06, CP-12 y CP-13 se debe comparar interfaz, registro de base de datos y contenido del almacenamiento.
