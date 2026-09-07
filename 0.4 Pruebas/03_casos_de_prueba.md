# Casos de prueba

Todos los casos están inicialmente en estado **No ejecutado**. Las cuentas, nombres y documentos mencionados son ficticios.

## CP-01 - Inicio de sesión válido

- Prioridad: crítica.
- Precondición: existe el usuario activo `usuario_demo`.
- Datos: contraseña de prueba configurada para la cuenta.
- Pasos: abrir inicio de sesión, escribir credenciales válidas y seleccionar **Ingresar**.
- Resultado esperado: se crea una sesión y se muestra el tablero correspondiente al rol.
- Estado inicial: no ejecutado.

## CP-02 - Rechazo de credenciales inválidas

- Prioridad: crítica.
- Precondición: aplicación disponible.
- Datos: `usuario_demo` y una contraseña incorrecta.
- Pasos: enviar el formulario con la contraseña incorrecta.
- Resultado esperado: no se crea sesión, no se revela qué dato falló y se muestra un mensaje claro.
- Estado inicial: no ejecutado.

## CP-03 - Cierre de sesión

- Prioridad: crítica.
- Precondición: sesión iniciada.
- Pasos: seleccionar **Cerrar sesión** y volver manualmente a una URL protegida.
- Resultado esperado: la sesión termina y la URL protegida redirige al inicio de sesión.
- Estado inicial: no ejecutado.

## CP-04 - Bloqueo de una función administrativa

- Prioridad: crítica.
- Precondición: sesión iniciada con rol `usuario`.
- Pasos: solicitar directamente la ruta de administración o reporte global.
- Resultado esperado: el servidor rechaza la operación con redirección segura o código 403; no expone información administrativa.
- Estado inicial: no ejecutado.

## CP-05 - Carga correcta de un documento

- Prioridad: alta.
- Precondición: usuario autenticado y almacenamiento disponible.
- Datos: `contrato_001.txt`, título `Contrato de suministro 001`, categoría `Contrato`.
- Pasos: abrir carga, completar metadatos, elegir el archivo y guardar.
- Resultado esperado: se crea un registro, se conserva una copia con nombre interno seguro y el documento aparece en el listado autorizado.
- Estado inicial: no ejecutado.

## CP-06 - Validación de campos obligatorios

- Prioridad: alta.
- Precondición: usuario autenticado.
- Pasos: enviar la carga sin título o sin archivo.
- Resultado esperado: no se crea un registro ni un archivo huérfano; se señalan los campos obligatorios.
- Estado inicial: no ejecutado.

## CP-07 - Rechazo de extensión no permitida

- Prioridad: alta.
- Precondición: usuario autenticado.
- Datos: archivo ficticio con extensión `.exe`.
- Pasos: intentar cargarlo con metadatos válidos.
- Resultado esperado: la carga se rechaza, se informa cuáles formatos son válidos y no se guarda el archivo.
- Estado inicial: no ejecutado.

## CP-08 - Búsqueda por texto y categoría

- Prioridad: alta.
- Precondición: existen documentos de las tres categorías.
- Pasos: buscar `suministro` y filtrar por `Contrato`.
- Resultado esperado: se muestran solo documentos visibles que cumplen ambos criterios; no aparecen elementos archivados salvo que el filtro lo solicite.
- Estado inicial: no ejecutado.

## CP-09 - Búsqueda sin coincidencias

- Prioridad: media.
- Precondición: usuario autenticado.
- Datos: texto `ZZZ-SIN-COINCIDENCIA`.
- Pasos: realizar la búsqueda.
- Resultado esperado: se presenta una lista vacía con un mensaje útil, sin error del servidor.
- Estado inicial: no ejecutado.

## CP-10 - Descarga autorizada

- Prioridad: crítica.
- Precondición: existe un documento accesible para el usuario.
- Pasos: abrir el detalle y seleccionar **Descargar**.
- Resultado esperado: se entrega el archivo correcto, con tipo de contenido y nombre de descarga apropiados; queda evidencia de auditoría si esa función está habilitada.
- Estado inicial: no ejecutado.

## CP-11 - Descarga no autorizada

- Prioridad: crítica.
- Precondición: existe un documento que el usuario actual no puede consultar.
- Pasos: solicitar directamente la URL o identificador de descarga.
- Resultado esperado: el servidor niega el acceso y no revela ruta física, nombre interno ni contenido.
- Estado inicial: no ejecutado.

## CP-12 - Edición de metadatos

- Prioridad: alta.
- Precondición: administrador autenticado y documento existente.
- Pasos: cambiar título, categoría y descripción; guardar; volver al detalle.
- Resultado esperado: los nuevos metadatos persisten, el archivo original permanece asociado y el cambio puede auditarse.
- Estado inicial: no ejecutado.

## CP-13 - Archivo y restauración lógica

- Prioridad: alta.
- Precondición: administrador autenticado y documento activo.
- Pasos: archivar, revisar el listado normal, activar filtro de archivados y restaurar.
- Resultado esperado: el documento desaparece del listado activo, aparece entre archivados y vuelve a activo después de restaurarlo, sin perder el archivo.
- Estado inicial: no ejecutado.

## CP-14 - Reporte administrativo

- Prioridad: media.
- Precondición: administrador autenticado y documentos de prueba registrados.
- Pasos: abrir reportes, elegir un intervalo válido y generar el resumen.
- Resultado esperado: se presentan totales coherentes por categoría y estado; el intervalo aplicado es visible y el acceso está limitado al administrador.
- Estado inicial: no ejecutado.

## CP-15 - Función futura de IA deshabilitada

- Prioridad: baja en esta versión.
- Precondición: prototipo sin proveedor ni clave de IA.
- Pasos: revisar configuración, interfaz y documentación.
- Resultado esperado: no se realizan llamadas externas; cualquier opción futura de clasificación o resumen se muestra como pendiente o permanece ausente; el flujo documental funciona sin IA.
- Estado inicial: pendiente por alcance.
