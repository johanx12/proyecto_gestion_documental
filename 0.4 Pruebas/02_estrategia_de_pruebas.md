# Estrategia de pruebas

## Enfoque

La estrategia combina pruebas manuales de interfaz con validaciones automatizables de rutas y lógica de negocio. Para una primera versión académica se priorizan los flujos que ponen en riesgo la confidencialidad o la conservación de documentos.

## Niveles de prueba

| Nivel | Propósito | Ejemplos |
|---|---|---|
| Unitaria | Revisar funciones aisladas. | Validar extensión, generar nombre seguro y calcular filtros por fecha. |
| Integración | Revisar comunicación entre componentes. | Formulario, base de datos y almacenamiento físico. |
| Sistema | Validar un flujo de principio a fin. | Iniciar sesión, cargar, localizar y descargar un documento. |
| Aceptación | Confirmar utilidad para el usuario. | El administrador obtiene el reporte y el usuario comprende los mensajes. |

## Tipos de prueba

- Funcionales: se verifica cada acción observable del portal.
- Autorización: se intenta acceder a opciones con un rol incorrecto.
- Validación: se prueban campos vacíos, extensiones no permitidas, tamaño y búsquedas sin resultados.
- Persistencia: se confirma la relación entre registro y archivo almacenado.
- Usabilidad básica: se revisan etiquetas, navegación, mensajes y adaptación a pantalla pequeña.
- Desempeño local: se mide de forma orientativa la carga de listas y búsquedas con datos de prueba.
- Recuperación básica: se documenta la restauración de copia de base de datos y archivos.

## Priorización

| Prioridad | Interpretación | Funciones |
|---|---|---|
| Crítica | Un fallo detiene el uso o expone información. | Autenticación, permisos, almacenamiento, descarga privada. |
| Alta | Un fallo impide la operación principal. | Carga, búsqueda, metadatos, archivo lógico. |
| Media | Existe alternativa temporal. | Reportes, exportación y filtros secundarios. |
| Baja | Afecta presentación sin bloquear. | Estilos, textos y detalles visuales. |

## Técnicas de diseño

- Partición de equivalencia: archivo permitido frente a archivo no permitido.
- Valores límite: campo vacío, longitud máxima y tamaño máximo del archivo.
- Tabla de decisión: combinación de rol, propietario y estado del documento.
- Transición de estados: activo, archivado y restaurado.
- Camino feliz y caminos alternos: operación correcta, validación fallida y recurso inexistente.

## Preparación de datos

Se usarán únicamente personas y organizaciones ficticias. Los 30 documentos de muestra se dividen en contratos, facturas e informes. El contenido no contiene números de identificación, direcciones, teléfonos ni datos bancarios reales.

## Evidencias

Por cada caso ejecutado se recomienda guardar:

1. Identificador del caso y versión de la aplicación.
2. Fecha, responsable y sistema operativo.
3. Datos utilizados.
4. Captura del resultado o respuesta HTTP relevante.
5. Estado: aprobado, fallido o bloqueado.
6. Identificador del defecto cuando aplique.

Las evidencias deben guardarse fuera del repositorio si incluyen secretos o datos del ambiente. Para la entrega académica se aceptan evidencias saneadas en una carpeta `test-results` ignorada por Git.

## Automatización sugerida

Cuando el código esté estable, se pueden automatizar con `pytest` los casos CP-01 a CP-12 usando una base temporal y un directorio temporal. La automatización no debe depender de una API de IA. El caso CP-15 queda pendiente por alcance.

## Ciclo de defectos

`Nuevo -> Confirmado -> En corrección -> Listo para repetir -> Cerrado`

Si el equipo decide no corregir un defecto, debe pasar a `Aceptado` e incluir una justificación y el impacto conocido.
