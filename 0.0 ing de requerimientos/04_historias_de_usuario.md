# Historias de usuario

## HU-01 - Iniciar sesión

**Como** usuario registrado, **quiero** iniciar sesión, **para** acceder a las funciones autorizadas.

**Criterios de aceptación**

1. Dado un usuario activo con credenciales válidas, cuando envía el formulario, entonces accede al dashboard.
2. Dadas credenciales inválidas, cuando intenta ingresar, entonces permanece en el formulario y recibe un mensaje general.
3. Dado un usuario inactivo, cuando intenta ingresar, entonces el acceso es rechazado.

Relacionada con: RF-01, RN-01.

## HU-02 - Gestionar usuarios

**Como** administrador, **quiero** registrar y mantener usuarios, **para** controlar quién accede al sistema.

**Criterios de aceptación**

1. Dado un formulario válido, cuando el administrador registra un usuario, entonces el usuario queda disponible para iniciar sesión.
2. Dado un identificador ya registrado, cuando intenta guardarlo, entonces el sistema informa la duplicidad.
3. Dado un usuario normal, cuando intenta abrir esta función, entonces el sistema rechaza el acceso.
4. Dado que solo queda un administrador activo, cuando se intenta desactivarlo, entonces la operación es rechazada.

Relacionada con: RF-03, RF-16, RN-02, RN-03, RN-04.

## HU-03 - Crear un repositorio

**Como** administrador, **quiero** crear un repositorio con nombre y descripción, **para** agrupar documentos relacionados.

**Criterios de aceptación**

1. Dado un nombre válido, cuando se guarda, entonces el repositorio aparece en el listado.
2. Dado un nombre vacío, cuando se envía, entonces el sistema solicita corregirlo.
3. Dado un usuario sin rol administrador, cuando intenta crear un repositorio, entonces la operación es rechazada.

Relacionada con: RF-04, RN-05.

## HU-04 - Consultar repositorios

**Como** usuario autorizado, **quiero** consultar los repositorios, **para** localizar el grupo documental que necesito.

**Criterios de aceptación**

1. Dada una sesión válida, cuando abre la página de repositorios, entonces se muestran los repositorios registrados.
2. Dado un repositorio existente, cuando abre su detalle, entonces ve su descripción y documentos.
3. Dada una sesión ausente, cuando intenta acceder, entonces se solicita autenticación.

Relacionada con: RF-05, RF-09.

## HU-05 - Cargar un documento

**Como** usuario autorizado, **quiero** cargar un PDF, DOCX o TXT, **para** conservarlo en el repositorio correcto.

**Criterios de aceptación**

1. Dado un archivo permitido menor o igual a 10 MB, cuando se envía a un repositorio existente, entonces el archivo queda almacenado y sus metadatos quedan registrados.
2. Dado un archivo con extensión no permitida, cuando se envía, entonces se rechaza y se explica el formato aceptado.
3. Dado un archivo que supera el límite, cuando se envía, entonces se rechaza antes de completar el registro.
4. Dado un fallo de almacenamiento, cuando ocurre, entonces no queda un registro incompleto y el error se registra.

Relacionada con: RF-06, RF-07, RF-08, RF-15, RN-06 a RN-09.

## HU-06 - Buscar documentos

**Como** usuario autorizado, **quiero** buscar por nombre o metadatos, **para** encontrar un documento sin recorrer todas las carpetas.

**Criterios de aceptación**

1. Dado un término con coincidencias, cuando se ejecuta la búsqueda, entonces se muestran los documentos coincidentes.
2. Dado un término sin coincidencias, cuando se ejecuta la búsqueda, entonces se informa que no existen resultados.
3. Dado un filtro de formato o repositorio, cuando se aplica, entonces la lista solo muestra los documentos correspondientes.
4. Dado un término vacío, cuando se consulta, entonces se muestra el listado sin producir error.

Relacionada con: RF-12, RF-13.

## HU-07 - Descargar un documento

**Como** usuario autorizado, **quiero** descargar un documento, **para** utilizar su contenido fuera de la aplicación.

**Criterios de aceptación**

1. Dado un registro y archivo físico existentes, cuando el usuario descarga, entonces recibe el archivo con su nombre original.
2. Dado un archivo físico ausente, cuando intenta descargar, entonces recibe un mensaje controlado y se registra el error.
3. Dada una sesión ausente, cuando se solicita la descarga, entonces el acceso es rechazado.

Relacionada con: RF-10, RF-15, RN-10.

## HU-08 - Eliminar un documento

**Como** administrador, **quiero** eliminar un documento, **para** retirar información que ya no debe permanecer disponible.

**Criterios de aceptación**

1. Dado un documento existente, cuando el administrador confirma, entonces se retiran el archivo y su registro.
2. Dado un usuario normal, cuando intenta eliminar, entonces la operación es rechazada.
3. Dada una solicitud sin confirmación, cuando se presenta, entonces no se elimina información.
4. Dado un fallo durante la eliminación, entonces se informa el error y queda registro para revisión.

Relacionada con: RF-11, RF-15, RF-16, RN-11.

## HU-09 - Consultar indicadores

**Como** usuario autorizado, **quiero** ver indicadores básicos, **para** conocer el estado general del repositorio documental.

**Criterios de aceptación**

1. Dada una sesión válida, cuando se abre el dashboard, entonces se muestran totales de repositorios y documentos.
2. Dado que existen documentos, cuando se abre el dashboard, entonces la suma por formato coincide con el total registrado.
3. Dado que no existen documentos, cuando se abre el dashboard, entonces los indicadores muestran cero sin error.

Relacionada con: RF-14, RN-13.

## HU-10 - Revisar errores

**Como** administrador, **quiero** consultar errores registrados, **para** identificar fallos de carga o descarga.

**Criterios de aceptación**

1. Dado un error registrado, cuando el administrador abre el registro, entonces ve fecha, operación y descripción.
2. Dado un usuario normal, cuando intenta consultar el registro, entonces el acceso es rechazado.
3. Dado que no existen errores, cuando se consulta, entonces se muestra una lista vacía sin fallo.

Relacionada con: RF-15, RF-16, RN-14.

## Historias relacionadas con inteligencia artificial

**Pendiente de implementación.**

No se redactan historias ni criterios para procesamiento, clasificación, resumen, extracción o consulta mediante IA hasta que el equipo decida incorporar esas funciones.
