# Casos de uso

## 1. Catálogo

| ID | Caso de uso | Actor principal | Requisitos |
|---|---|---|---|
| CU-01 | Autenticarse | ADM, USR | RF-01, RF-02 |
| CU-02 | Gestionar usuarios | ADM | RF-03, RF-16 |
| CU-03 | Gestionar repositorios | ADM | RF-04, RF-05, RF-16 |
| CU-04 | Cargar documento | ADM, USR | RF-06, RF-07, RF-08, RF-15 |
| CU-05 | Consultar y buscar documentos | ADM, USR | RF-09, RF-12, RF-13 |
| CU-06 | Descargar documento | ADM, USR | RF-10, RF-15 |
| CU-07 | Eliminar documento | ADM | RF-11, RF-15, RF-16 |
| CU-08 | Consultar dashboard | ADM, USR | RF-14 |
| CU-09 | Consultar registro de errores | ADM | RF-15, RF-16 |

## 2. CU-01 - Autenticarse

| Campo | Descripción |
|---|---|
| Objetivo | Crear una sesión para un usuario válido y permitir su cierre. |
| Precondiciones | El usuario existe y está activo. |
| Disparador | El usuario envía el formulario de inicio de sesión. |
| Poscondición exitosa | Existe una sesión asociada al usuario y se muestra el dashboard. |
| Poscondición alterna | No se crea la sesión y se informa que no fue posible ingresar. |

**Flujo principal**

1. El usuario abre la pantalla de acceso.
2. El sistema solicita identificador y contraseña.
3. El usuario envía sus credenciales.
4. El sistema localiza al usuario activo.
5. El sistema verifica el hash de la contraseña.
6. El sistema crea la sesión.
7. El sistema muestra el dashboard.

**Flujos alternos**

- A1. Faltan datos: el sistema marca los campos obligatorios.
- A2. Credenciales inválidas: el sistema rechaza el acceso con un mensaje general.
- A3. Usuario inactivo: el sistema rechaza el acceso.

## 3. CU-02 - Gestionar usuarios

| Campo | Descripción |
|---|---|
| Objetivo | Mantener las cuentas y roles de acceso. |
| Precondiciones | El actor inició sesión como administrador. |
| Poscondición exitosa | El usuario queda creado, actualizado o desactivado. |

**Flujo principal de creación**

1. El administrador abre la gestión de usuarios.
2. Selecciona crear usuario.
3. Registra nombre, identificador, contraseña inicial y rol.
4. El sistema valida campos y unicidad.
5. El sistema genera el hash de la contraseña.
6. El sistema guarda el usuario y confirma la operación.

**Flujos alternos**

- A1. Identificador duplicado: el sistema no guarda y señala la duplicidad.
- A2. Datos incompletos: el sistema solicita corregirlos.
- A3. Último administrador activo: el sistema impide su desactivación.
- A4. Rol insuficiente: el sistema rechaza el acceso.

## 4. CU-03 - Gestionar repositorios

| Campo | Descripción |
|---|---|
| Objetivo | Crear y mantener agrupaciones documentales. |
| Precondiciones | El actor inició sesión como administrador. |
| Poscondición exitosa | El repositorio queda creado, actualizado o eliminado. |

**Flujo principal de creación**

1. El administrador abre el listado.
2. Selecciona nuevo repositorio.
3. Registra nombre y descripción.
4. El sistema valida y guarda.
5. El sistema muestra el detalle del repositorio.

**Flujos alternos**

- A1. Nombre vacío: se solicita corregir.
- A2. Eliminación con documentos: se rechaza la operación y se informa el motivo.
- A3. Repositorio inexistente: se muestra una respuesta controlada.

## 5. CU-04 - Cargar documento

| Campo | Descripción |
|---|---|
| Objetivo | Almacenar un archivo permitido y registrar sus metadatos. |
| Precondiciones | Sesión válida y repositorio existente. |
| Disparador | El usuario envía el formulario de carga. |
| Poscondición exitosa | El archivo existe en almacenamiento y su registro queda en estado almacenado. |
| Poscondición alterna | No quedan datos parciales y se informa el error. |

**Flujo principal**

1. El usuario abre el repositorio.
2. Selecciona cargar documento.
3. Selecciona un PDF, DOCX o TXT e ingresa una descripción opcional.
4. El sistema valida presencia, extensión y tamaño.
5. El sistema crea un nombre físico seguro y único.
6. El sistema guarda el archivo.
7. El sistema registra sus metadatos.
8. El sistema confirma y actualiza la lista.

**Flujos alternos**

- A1. Formato no admitido: se rechaza antes de almacenar.
- A2. Tamaño mayor a 10 MB: se rechaza antes de almacenar.
- A3. Repositorio inexistente: se cancela la operación.
- A4. Error al guardar: se limpia cualquier resultado parcial y se registra el error.

## 6. CU-05 - Consultar y buscar documentos

| Campo | Descripción |
|---|---|
| Objetivo | Localizar y consultar metadatos de documentos. |
| Precondiciones | Sesión válida. |
| Poscondición | Se presenta el listado filtrado o un estado sin resultados. |

**Flujo principal**

1. El usuario abre el listado de documentos.
2. Ingresa un término y, si lo requiere, selecciona repositorio o formato.
3. El sistema valida los parámetros.
4. El sistema consulta nombre, descripción, formato y repositorio.
5. El sistema muestra las coincidencias.
6. El usuario abre la ficha de un resultado.

**Flujos alternos**

- A1. Término vacío: se muestran todos los registros permitidos.
- A2. Sin coincidencias: se muestra un mensaje y los filtros activos.

## 7. CU-06 - Descargar documento

| Campo | Descripción |
|---|---|
| Objetivo | Entregar al usuario un archivo registrado. |
| Precondiciones | Sesión válida, registro existente y archivo físico disponible. |
| Poscondición exitosa | El navegador recibe el archivo con su nombre original. |

**Flujo principal**

1. El usuario abre la ficha del documento.
2. Selecciona descargar.
3. El sistema verifica el registro y la ruta segura.
4. El sistema entrega el archivo como adjunto.

**Flujos alternos**

- A1. Registro inexistente: se informa que el recurso no existe.
- A2. Archivo físico ausente: se informa el problema y se registra el error.

## 8. CU-07 - Eliminar documento

| Campo | Descripción |
|---|---|
| Objetivo | Retirar un documento del sistema. |
| Precondiciones | Sesión de administrador y documento existente. |
| Poscondición exitosa | El archivo físico y el registro dejan de estar disponibles. |

**Flujo principal**

1. El administrador abre la ficha.
2. Selecciona eliminar.
3. El sistema solicita confirmación.
4. El administrador confirma.
5. El sistema elimina de forma coordinada el archivo y el registro.
6. El sistema confirma la operación.

**Flujos alternos**

- A1. No hay confirmación: no se ejecutan cambios.
- A2. Rol insuficiente: se rechaza la operación.
- A3. Fallo de eliminación: se registra el error y se informa el estado real.

## 9. CU-08 - Consultar dashboard

| Campo | Descripción |
|---|---|
| Objetivo | Presentar un resumen cuantitativo del repositorio. |
| Precondiciones | Sesión válida. |
| Poscondición | Se muestran indicadores calculados con la base de datos. |

**Flujo principal**

1. El usuario inicia sesión o abre el dashboard.
2. El sistema cuenta repositorios y documentos.
3. El sistema agrupa los documentos por formato y estado.
4. El sistema muestra los indicadores.

## 10. CU-09 - Consultar registro de errores

| Campo | Descripción |
|---|---|
| Objetivo | Apoyar el diagnóstico de fallos operativos. |
| Precondiciones | Sesión de administrador. |
| Poscondición | Se muestra el listado de errores ordenado por fecha. |

**Flujo principal**

1. El administrador abre el registro.
2. El sistema consulta los eventos de error.
3. El sistema muestra fecha, operación y detalle.

## 11. Casos de uso de inteligencia artificial

**Pendiente de implementación.**

No se especifican flujos de IA en esta versión.
