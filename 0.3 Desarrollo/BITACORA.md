# Bitácora de desarrollo

## Información del proyecto

- Proyecto: Sistema de Gestión y Análisis Documental.
- Fase: 0.3 Desarrollo.
- Tipo: prototipo web académico.
- Tecnología: Python, Flask, SQLite, HTML y CSS.

## Registro de avances

| Fecha | Actividad | Resultado | Estado |
|---|---|---|---|
| 2026-09-06 | Preparación de la estructura del proyecto | Se organizaron aplicación, servicios, plantillas, estilos e instancia local. | Completado |
| 2026-09-06 | Modelo de persistencia | Se crearon tablas para usuarios, repositorios, documentos y bitácora. | Completado |
| 2026-09-06 | Autenticación | Se agregó registro, acceso, cierre de sesión y hash de contraseña. | Completado |
| 2026-09-06 | Gestión de repositorios | Se agregó creación, consulta, edición y eliminación controlada. | Completado |
| 2026-09-06 | Gestión de documentos | Se agregó carga, listado, edición de metadatos, descarga y eliminación. | Completado |
| 2026-09-06 | Validaciones | Se validaron formato y tamaño del archivo antes de almacenarlo. | Completado |
| 2026-09-06 | Consulta | Se agregó búsqueda simple por metadatos. | Completado |
| 2026-09-06 | Interfaz | Se crearon vistas adaptables para acceso, panel, repositorios y documentos. | Completado |
| 2026-09-06 | Integración de IA | Se creó únicamente el archivo de extensión, sin modelo, API, claves ni procesamiento. | Reemplazado el 2026-09-07 |
| 2026-09-07 | Extracción de contenido | Se implementó `services/extractor.py` para PDF (pypdf), DOCX (python-docx) y TXT, con normalización y fragmentación con solape. | Completado |
| 2026-09-07 | Integración con Google Gemini | Se implementó `services/ai_service.py`: clasificación, resumen y extracción con `responseSchema`, embeddings de 768 dimensiones y respuesta del asistente. | Completado |
| 2026-09-07 | Orquestación del flujo | Se implementó `services/procesamiento.py` con estados `Pendiente`, `Procesado` y `Error` y registro del detalle de cada falla. | Completado |
| 2026-09-07 | Búsqueda semántica y RAG | Se implementó `services/rag.py` con similitud coseno sobre la tabla `fragmentos`. | Completado |
| 2026-09-07 | Ampliación del modelo de datos | Se agregaron `fragmentos`, `consultas_ia`, el nivel de la bitácora y las columnas de análisis en `documentos`. | Completado |
| 2026-09-07 | Interfaz de IA | Se agregaron la ficha del documento, el asistente conversacional, el selector de modo de búsqueda y los indicadores de estado en el panel. | Completado |
| 2026-09-07 | Corpus de prueba | Se regeneraron los 30 documentos con contenido realista en TXT, DOCX y PDF mediante `scripts/generar_documentos_prueba.py`. | Completado |
| 2026-09-07 | Pruebas automatizadas | 28 pruebas con dobles de IA y 3 pruebas de integración real contra la API. Todas en verde. | Completado |
| 2026-09-07 | Ampliación de formatos | Se agregaron DOC, ODT, XLSX, PPTX, RTF, HTML, CSV, JSON, XML e imágenes, sin dependencias nuevas: los formatos de Office se leen con `zipfile` y `ElementTree`. | Completado |
| 2026-09-07 | OCR con IA | Cuando la extracción local no obtiene texto, el archivo se envía al modelo multimodal para transcribirlo. Verificado contra la API real. | Completado |
| 2026-09-07 | Carga múltiple y cola | El asistente acepta varios archivos a la vez y el análisis avanza en un trabajador en segundo plano. | Completado |

## Decisiones técnicas

1. Se utilizó SQLite porque permite reproducir el prototipo sin instalar un servidor de base de datos.
2. Los archivos se guardan en `instance/uploads` con nombres aleatorios para evitar colisiones y reducir riesgos asociados al nombre original.
3. La categoría la asigna la IA al cargar el archivo; el usuario puede corregirla desde la edición del documento.
4. La búsqueda recorre el contenido extraído y, en modo semántico, los vectores de los fragmentos.
5. El primer usuario recibe rol de administrador para facilitar la demostración universitaria.
6. Se eligió `gemini-3.5-flash-lite` porque el modelo mayor devolvió `503` de forma intermitente durante las pruebas; el modelo es configurable por variable de entorno.
7. Los vectores se guardan como JSON en SQLite en lugar de usar una base vectorial: para decenas de documentos el coste es despreciable y el despliegue sigue siendo un solo archivo.
8. El procesamiento es síncrono al cargar el documento. Con archivos grandes o cargas masivas convendría una cola de trabajos, pero eso añadiría infraestructura innecesaria para el alcance académico.

## Trabajo previsto para una siguiente versión

- OCR para PDF escaneados sin capa de texto.
- Cola de procesamiento asíncrona para cargas masivas.
- Permisos por repositorio compartido y recuperación de contraseña.
- Protección CSRF y análisis antivirus del archivo cargado.
- Paginación del listado y copias de seguridad automáticas.
