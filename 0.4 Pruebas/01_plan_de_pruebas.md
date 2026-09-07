# Plan de pruebas

## 1. Identificación

- Proyecto: Portal de Gestión Documental.
- Versión objeto de prueba: prototipo académico inicial.
- Documento: plan de pruebas funcionales y no funcionales.
- Estado: preparado para ejecución.

## 2. Objetivo

Comprobar que el portal permite registrar usuarios, autenticar roles, almacenar documentos con metadatos, consultarlos, descargarlos, cambiar su estado y generar información útil para administración sin exponer archivos a personas no autorizadas.

## 3. Alcance

Se planean pruebas sobre:

- inicio y cierre de sesión;
- control de acceso por rol;
- carga de archivos y registro de metadatos;
- validación de campos obligatorios, extensiones y tamaño;
- listado, búsqueda y filtros;
- consulta y descarga de documentos;
- edición de metadatos;
- archivo y restauración lógica;
- generación de reporte administrativo;
- registro de auditoría;
- manejo básico de errores, usabilidad y tiempos de respuesta locales.

Quedan fuera del alcance de esta versión:

- integración con servicios de IA;
- firma electrónica con validez jurídica;
- almacenamiento distribuido en nube;
- pruebas de carga masiva de producción;
- pruebas de penetración profesionales;
- recuperación ante desastres en infraestructura real.

## 4. Elementos que se probarán

1. Aplicación web construida con Python y Flask.
2. Persistencia local en SQLite.
3. Carpeta privada de almacenamiento de archivos.
4. Formularios, vistas y rutas HTTP.
5. Perfiles `usuario` y `administrador`.
6. Exportación o visualización del reporte, según lo implementado.

## 5. Ambiente propuesto

- Equipo local con Windows, Linux o macOS.
- Python 3.11 o superior.
- Navegador actualizado.
- Base de datos SQLite exclusiva para pruebas.
- Directorio de archivos exclusivo para pruebas.
- Variables definidas a partir de `.env.example`.
- Datos ficticios ubicados en `11_repositorio_pruebas/datos_prueba`.

La base de datos y el almacenamiento de pruebas deben estar separados de cualquier ambiente con información real.

## 6. Roles sugeridos

| Rol de prueba | Responsabilidad |
|---|---|
| Líder del proyecto | Aprueba alcance y criterios de salida. |
| Probador | Ejecuta casos, conserva evidencias y registra defectos. |
| Desarrollador | Corrige defectos y apoya la reproducción. |
| Usuario representante | Valida claridad del flujo y criterios de aceptación. |

En un equipo universitario una persona puede cumplir más de un rol, pero debe dejar identificada la actividad realizada.

## 7. Criterios de entrada

- El proyecto instala sus dependencias sin errores.
- La aplicación inicia en un ambiente local.
- La base de datos de pruebas puede inicializarse.
- Existe al menos una cuenta de administrador y una de usuario.
- Los 30 archivos ficticios están disponibles.
- Los casos tienen datos y resultado esperado definidos.

## 8. Criterios de salida

- Se ejecutan los casos críticos de autenticación, autorización, carga, búsqueda y descarga.
- No quedan defectos críticos abiertos.
- Los defectos altos tienen corrección o justificación académica documentada.
- Cada ejecución tiene fecha, responsable, resultado y evidencia.
- La matriz requisito-prueba está actualizada.

## 9. Criterios de suspensión y reanudación

La jornada se suspende si la aplicación no inicia, la base de datos no puede crearse, se pierde el ambiente de prueba o un defecto impide ejecutar varios casos. Se reanuda cuando el bloqueo se corrige, se reinicia el ambiente y se registra la versión evaluada.

## 10. Riesgos

| Riesgo | Probabilidad | Impacto | Tratamiento |
|---|---|---|---|
| Diferencias entre sistemas operativos | Media | Media | Probar rutas con `pathlib` y documentar el SO. |
| Archivos grandes llenan el disco | Media | Alta | Limitar tamaño y vigilar el almacenamiento. |
| Datos de una prueba afectan otra | Media | Media | Reiniciar la base o usar identificadores únicos. |
| Acceso directo a archivos privados | Baja | Alta | Servir archivos solo tras validar sesión y permisos. |
| Alcance de IA confuso | Media | Media | Mantenerla marcada como pendiente y sin credenciales. |

## 11. Cronograma sugerido

| Actividad | Duración estimada |
|---|---:|
| Preparar ambiente y datos | 2 horas |
| Ejecutar pruebas funcionales | 4 horas |
| Ejecutar pruebas de roles y seguridad básica | 2 horas |
| Revisar usabilidad y desempeño local | 1 hora |
| Corregir y repetir casos fallidos | 3 horas |
| Consolidar evidencias y conclusiones | 2 horas |

## 12. Entregables

- Registro de ejecución completo.
- Capturas o archivos de evidencia sin datos reales.
- Registro de defectos actualizado.
- Matriz de trazabilidad actualizada.
- Conclusión final firmada por el equipo académico.
