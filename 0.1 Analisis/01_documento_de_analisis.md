# Documento de análisis

## Problema

La empresa recibe solicitudes y documentos de sus clientes por distintos medios. La información queda dispersa, es difícil conocer el estado de cada atención y los administradores no cuentan con un reporte mensual sencillo.

## Solución propuesta

Un portal web académico centraliza usuarios, repositorios, carpetas y documentos. Permite registrar la información en SQLite, consultar por metadatos, descargar archivos autorizados y revisar métricas. La integración con IA queda como punto de extensión para una versión futura, sin llamadas externas en esta entrega.

## Alcance de la versión 0.1

- Registro e inicio de sesión con dos roles: administrador y usuario.
- Creación y mantenimiento de repositorios.
- Carga de archivos PDF, DOCX y TXT, con metadatos y categoría.
- Consulta, búsqueda, descarga y eliminación con control de permisos.
- Tablero con conteos y bitácora básica.
- Base SQLite y almacenamiento local para facilitar la práctica universitaria.

## Fuera de alcance temporal

El procesamiento automático de contenido, clasificación inteligente, resumen, extracción avanzada y preguntas en lenguaje natural quedan documentados como pendientes. Tampoco se incluyen todavía correo, alta disponibilidad ni despliegue productivo.

## Criterios de aceptación

1. Un usuario puede crear una cuenta e iniciar sesión.
2. Un usuario autenticado puede crear un repositorio y cargar un PDF, DOCX o TXT.
3. El sistema guarda los metadatos y permite buscar por título, descripción, nombre o categoría.
4. Un usuario no puede descargar documentos de otro propietario.
5. Un administrador puede consultar el tablero y la bitácora.
6. Las operaciones inválidas muestran un mensaje entendible y no dejan archivos huérfanos.

