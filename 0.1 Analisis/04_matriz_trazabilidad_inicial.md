# Matriz de trazabilidad inicial

| Objetivo | Requisito | Historia | Diseño | Prueba |
|---|---|---|---|---|
| Centralizar documentos | RF-01..RF-04 | HU-01..HU-04 | Tablas `usuarios`, `repositorios`, `documentos` | CP-01, CP-05, CP-10 |
| Encontrar información | RF-05 | HU-05 | Índices y ruta `/buscar` | CP-08, CP-09 |
| Proteger la información | RF-06 | HU-06 | Sesión y validación de propietario | CP-02, CP-04, CP-11 |
| Dar seguimiento | RF-09..RF-10 | HU-07 | `bitacora` y tablero | CP-14 |
| Preparar evolución IA | RF-12..RF-15 | HU-08 | `services/ai_service.py` como extensión | CP-15 |

