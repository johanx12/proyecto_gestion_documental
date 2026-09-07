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
| 2026-09-06 | Validaciones | Se limitaron formatos a PDF, DOCX y TXT y el tamaño a 10 MB. | Completado |
| 2026-09-06 | Consulta | Se agregó búsqueda simple por metadatos. | Completado |
| 2026-09-06 | Interfaz | Se crearon vistas adaptables para acceso, panel, repositorios y documentos. | Completado |
| 2026-09-06 | Integración de IA | Se creó únicamente el archivo de extensión, sin modelo, API, claves ni procesamiento. | Pendiente por alcance |

## Decisiones técnicas

1. Se utilizó SQLite porque permite reproducir el prototipo sin instalar un servidor de base de datos.
2. Los archivos se guardan en `instance/uploads` con nombres aleatorios para evitar colisiones y reducir riesgos asociados al nombre original.
3. La categoría se asigna manualmente mientras la clasificación automática permanece pendiente.
4. La búsqueda se limita a metadatos hasta implementar extracción de texto e indexación.
5. El primer usuario recibe rol de administrador para facilitar la demostración universitaria.

## Trabajo previsto para una siguiente versión

- Extraer texto de PDF, DOCX y TXT.
- Integrar clasificación automática, resumen y extracción de datos.
- Incorporar preguntas sobre el contenido y búsqueda semántica.
- Agregar permisos por repositorio y recuperación de contraseña.
- Incorporar protección CSRF, pruebas de contenido y antivirus.
- Agregar paginación, copias de seguridad y despliegue reproducible.
