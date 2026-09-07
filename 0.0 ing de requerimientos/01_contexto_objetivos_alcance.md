# Contexto, objetivos y alcance

## 1. Identificación

| Campo | Valor |
|---|---|
| Proyecto | Sistema de Gestión Documental |
| Sigla | SGD |
| Tipo de solución | Aplicación web empresarial |
| Versión del documento | 1.0 |
| Estado | Línea base inicial |
| Público objetivo | Administradores y usuarios autorizados de una empresa |

## 2. Descripción del problema

La empresa conserva documentos en carpetas dispersas. Este manejo dificulta saber qué archivos existen, quién puede consultarlos, en qué repositorio se encuentran y cuál es su formato. También aumenta el tiempo empleado en búsquedas manuales y permite que se creen copias sin control.

La organización necesita un punto único de acceso para registrar usuarios, crear repositorios, cargar documentos, consultar su información, descargarlos y eliminarlos de forma controlada. La primera versión debe aceptar PDF, DOCX y TXT, conservar los archivos en almacenamiento local y registrar sus metadatos en una base de datos.

## 3. Necesidad y oportunidad de negocio

La necesidad principal es convertir una carpeta informal en un repositorio administrado mediante una aplicación. La oportunidad consiste en:

- centralizar los documentos y sus metadatos;
- disminuir el tiempo de localización de archivos;
- aplicar permisos básicos según el rol;
- conocer el volumen de información mediante indicadores;
- preparar una base técnica que pueda ampliarse en versiones futuras.

## 4. Pregunta orientadora adaptada

¿Cómo puede una empresa transformar una carpeta de documentos en un sistema web organizado, seguro y consultable, preparado para incorporar capacidades adicionales en el futuro?

## 5. Objetivo general

Diseñar, desarrollar, probar y documentar una aplicación web que permita administrar usuarios, repositorios y documentos PDF, DOCX y TXT, almacenando los archivos de manera controlada y sus metadatos en una base de datos.

## 6. Objetivos específicos

1. Implementar autenticación y autorización básica con roles de administrador y usuario.
2. Permitir la creación, consulta, actualización y eliminación de repositorios.
3. Permitir la carga, consulta, descarga y eliminación de documentos autorizados.
4. Validar el formato y el tamaño de los archivos antes de almacenarlos.
5. Registrar metadatos, estados y errores suficientes para controlar la operación.
6. Ofrecer búsqueda por nombre y metadatos.
7. Mostrar un dashboard con indicadores básicos del repositorio.
8. Documentar requisitos, diseño, desarrollo, pruebas e implementación con trazabilidad.

## 7. Alcance incluido en la primera versión

### Usuarios y acceso

- Inicio y cierre de sesión.
- Creación y gestión básica de usuarios por un administrador.
- Roles Administrador y Usuario.
- Contraseñas almacenadas mediante hash.
- Restricción de funciones administrativas por rol.

### Repositorios

- Crear, listar, consultar, editar y eliminar repositorios.
- Asignar nombre y descripción.
- Consultar los documentos asociados.

### Documentos

- Cargar PDF, DOCX y TXT.
- Validar extensión, tamaño máximo y nombre seguro.
- Guardar el archivo en almacenamiento local.
- Registrar nombre original, nombre almacenado, formato, tamaño, fecha, usuario, repositorio y estado.
- Listar, consultar, descargar y eliminar documentos.
- Buscar por nombre, descripción, formato y repositorio.

### Información para control

- Dashboard con totales de repositorios y documentos.
- Distribución de documentos por formato y estado.
- Registro básico de eventos y errores.

### Calidad y entrega

- Código fuente versionado con Git.
- Base de datos reproducible.
- Pruebas sencillas para los flujos principales.
- Manuales de instalación, uso y administración.

## 8. Exclusiones de la primera versión

- Aplicación móvil nativa.
- Integración con almacenamiento en la nube.
- Edición del contenido de documentos desde el navegador.
- Firma digital y control documental regulado.
- Flujos de aprobación multinivel.
- Versionado automático del contenido de un mismo archivo.
- Notificaciones por correo o mensajería.
- Recuperación automática de archivos eliminados.
- Alta disponibilidad y escalamiento horizontal.
- Integración con directorios empresariales.

## 9. Inteligencia artificial

**Pendiente de implementación.**

Se dejan fuera de esta versión el procesamiento mediante IA, la clasificación automática, los resúmenes, la extracción inteligente, los embeddings, la búsqueda semántica y las preguntas sobre documentos. No se define modelo, API, proveedor, flujo ni criterios de aceptación hasta que exista una decisión posterior del equipo.

## 10. Supuestos

- La solución se ejecutará inicialmente en un solo equipo o servidor.
- Los usuarios utilizarán un navegador moderno.
- Los documentos de prueba no contendrán datos personales reales sin autorización.
- El almacenamiento disponible será suficiente para el límite definido por archivo.
- La base de datos SQLite es adecuada para el volumen académico de la primera versión.

## 11. Dependencias

- Python y las dependencias indicadas por el proyecto.
- Acceso de escritura a la carpeta local de cargas.
- Navegador compatible.
- Disponibilidad del servidor Flask durante la demostración.

## 12. Criterios de éxito

La primera versión se considera aceptable cuando:

- un usuario autorizado puede iniciar sesión;
- un administrador puede gestionar usuarios y repositorios;
- se cargan, consultan, descargan y eliminan archivos PDF, DOCX y TXT;
- se rechazan formatos no admitidos;
- los metadatos persisten en SQLite;
- la búsqueda devuelve coincidencias por nombre o metadatos;
- el dashboard presenta conteos coherentes;
- las pruebas documentadas de la versión ejecutada tienen resultado verificable.
