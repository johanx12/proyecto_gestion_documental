# Matriz requisito-prueba

La matriz usa identificadores funcionales comunes del proyecto. Si el documento principal cambia un identificador, se debe conservar la relación y actualizar el código en ambas fuentes.

| Requisito | Descripción resumida | Caso(s) | Cobertura planeada |
|---|---|---|---|
| RF-01 | Autenticar usuario | CP-01, CP-02 | Positiva y negativa |
| RF-02 | Cerrar sesión y proteger rutas | CP-03 | Flujo completo |
| RF-03 | Autorizar funciones por rol | CP-04, CP-11 | Rol y acceso directo |
| RF-04 | Registrar documento y metadatos | CP-05, CP-06 | Camino feliz y validación |
| RF-05 | Validar tipo y tamaño de archivo | CP-07 | Tipo rechazado; tamaño se debe ampliar en ejecución |
| RF-06 | Consultar, buscar y filtrar | CP-08, CP-09 | Con y sin coincidencias |
| RF-07 | Ver y descargar documento | CP-10, CP-11 | Acceso permitido y denegado |
| RF-08 | Editar metadatos | CP-12 | Actualización persistente |
| RF-09 | Archivar y restaurar | CP-13 | Transiciones de estado |
| RF-10 | Generar reporte administrativo | CP-14 | Totales, fechas y rol |
| RF-11 | Registrar acciones relevantes | CP-10, CP-12, CP-13 | Auditoría asociada a operaciones |
| RF-IA-01 | Clasificar o resumir con IA | CP-15 | Pendiente, sin integración |
| RNF-01 | Proteger información y credenciales | CP-02, CP-04, CP-11 | Mensajes y autorización |
| RNF-02 | Mantener integridad entre BD y archivos | CP-05, CP-06, CP-12, CP-13 | Creación y cambios |
| RNF-03 | Ofrecer interfaz comprensible | CP-01, CP-05, CP-08, CP-09 | Revisión manual |
| RNF-04 | Responder en tiempo aceptable local | CP-08, CP-14 | Medición pendiente |

## Cobertura complementaria recomendada

En la ejecución se deben añadir casos para límite exacto de tamaño, doble envío del formulario, nombre de archivo con caracteres especiales, recurso inexistente, intervalo de fechas inválido y restauración desde respaldo. Estos casos amplían la cobertura sin cambiar el alcance funcional.
