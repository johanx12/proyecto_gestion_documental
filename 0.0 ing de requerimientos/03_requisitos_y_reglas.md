# Requisitos y reglas de negocio

## 1. Requisitos funcionales

| ID | Requisito verificable | Prioridad | Actor |
|---|---|---|---|
| RF-01 | El sistema debe permitir el inicio de sesión con usuario activo y contraseña válida. | Alta | ADM, USR |
| RF-02 | El sistema debe permitir cerrar la sesión activa. | Alta | ADM, USR |
| RF-03 | El administrador debe poder crear, consultar, editar y desactivar usuarios. | Alta | ADM |
| RF-04 | El administrador debe poder crear, consultar, editar y eliminar repositorios. | Alta | ADM |
| RF-05 | El sistema debe listar los repositorios disponibles para el usuario autenticado. | Alta | ADM, USR |
| RF-06 | El sistema debe permitir cargar un archivo PDF, DOCX o TXT en un repositorio existente. | Alta | ADM, USR |
| RF-07 | El sistema debe validar extensión, tamaño y presencia del archivo antes de guardarlo. | Alta | Sistema |
| RF-08 | El sistema debe registrar por cada documento su nombre original, nombre almacenado, formato, tamaño, fecha de carga, usuario, repositorio, descripción y estado. | Alta | Sistema |
| RF-09 | El sistema debe listar y mostrar el detalle de los documentos registrados. | Alta | ADM, USR |
| RF-10 | El sistema debe permitir descargar un documento existente. | Alta | ADM, USR |
| RF-11 | El administrador debe poder eliminar un documento después de una confirmación. | Alta | ADM |
| RF-12 | El sistema debe buscar documentos por coincidencia en nombre, descripción, formato o repositorio. | Media | ADM, USR |
| RF-13 | El sistema debe filtrar documentos al menos por repositorio y formato. | Media | ADM, USR |
| RF-14 | El sistema debe mostrar en el dashboard los totales de repositorios, documentos, formatos y estados. | Media | ADM, USR |
| RF-15 | El sistema debe registrar errores de carga y operaciones relevantes con fecha y detalle básico. | Media | Sistema |
| RF-16 | El sistema debe impedir que un usuario sin rol administrador acceda a la gestión de usuarios, eliminación o configuración. | Alta | Sistema |
| RF-17 | El sistema debe exponer un mecanismo de verificación de disponibilidad del servicio. | Baja | ADM |

## 2. Requisitos de inteligencia artificial

| ID | Elemento solicitado por la guía | Estado |
|---|---|---|
| RF-IA-01 | Procesamiento automático de documentos mediante IA | **Pendiente de implementación** |
| RF-IA-02 | Clasificación automática en categorías | **Pendiente de implementación** |
| RF-IA-03 | Generación de resumen por documento | **Pendiente de implementación** |
| RF-IA-04 | Extracción de información relevante | **Pendiente de implementación** |
| RF-IA-05 | Búsqueda semántica y consulta en lenguaje natural | **Pendiente de implementación** |

No se asignan criterios, componentes, estimación ni pruebas a estos elementos hasta que el equipo decida implementarlos.

## 3. Requisitos no funcionales

| ID | Categoría | Requisito verificable |
|---|---|---|
| RNF-01 | Usabilidad | Un usuario con conocimientos básicos debe poder cargar un archivo desde la página del repositorio siguiendo las etiquetas visibles del formulario. |
| RNF-02 | Compatibilidad | La interfaz debe funcionar en las versiones actuales de Chrome y Edge para escritorio. |
| RNF-03 | Rendimiento | Para un conjunto académico de hasta 1.000 registros, las páginas de listado deben responder en menos de 3 segundos en el entorno local de prueba. |
| RNF-04 | Seguridad | Las contraseñas deben almacenarse con hash y nunca en texto plano. |
| RNF-05 | Seguridad | Las rutas privadas deben exigir una sesión autenticada y las rutas administrativas deben validar el rol. |
| RNF-06 | Seguridad | El sistema debe normalizar el nombre almacenado y rechazar rutas o extensiones no autorizadas. |
| RNF-07 | Integridad | El registro de base de datos y el archivo físico deben corresponder; un fallo debe producir un mensaje y quedar registrado. |
| RNF-08 | Mantenibilidad | El código debe separar configuración, rutas, acceso a datos, plantillas y archivos estáticos. |
| RNF-09 | Portabilidad | El proyecto debe poder instalarse con Python y su archivo de dependencias en Windows, Linux o macOS. |
| RNF-10 | Recuperación | Debe existir un procedimiento documentado para respaldar SQLite y la carpeta de cargas. |
| RNF-11 | Privacidad | Los documentos de prueba no deben incluir datos personales reales sin autorización. |
| RNF-12 | Auditabilidad | Los eventos de error deben guardar fecha, tipo de operación y descripción suficiente para diagnóstico. |
| RNF-13 | Accesibilidad | Los formularios deben tener etiquetas asociadas y las acciones principales deben ser utilizables con teclado. |
| RNF-14 | Configuración | Las credenciales y valores sensibles no deben publicarse en el repositorio Git. |

## 4. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Solo un usuario activo puede iniciar sesión. |
| RN-02 | El correo o nombre de usuario debe ser único. |
| RN-03 | Debe existir al menos un administrador activo. |
| RN-04 | Solo el administrador puede crear, editar o desactivar usuarios. |
| RN-05 | Solo el administrador puede crear, editar o eliminar repositorios. |
| RN-06 | Un documento siempre pertenece a un repositorio. |
| RN-07 | Solo se admiten archivos con extensión PDF, DOCX o TXT. |
| RN-08 | El límite inicial por archivo es de 10 MB y debe estar centralizado en la configuración. |
| RN-09 | El nombre físico debe ser seguro y único, aunque se conserve el nombre original como metadato. |
| RN-10 | No se debe servir un archivo si el registro no existe o el archivo físico no está disponible. |
| RN-11 | La eliminación de un documento exige confirmación y permiso de administrador. |
| RN-12 | La eliminación de un repositorio no procede mientras contenga documentos; primero deben trasladarse o eliminarse. |
| RN-13 | Los indicadores del dashboard deben calcularse con datos registrados en la base de datos. |
| RN-14 | Los errores de almacenamiento o base de datos deben mostrarse con un mensaje general al usuario y un detalle técnico en el registro. |
| RN-15 | Los secretos, contraseñas y archivos locales de configuración no se incluyen en Git. |

## 5. Criterios generales de validación

- Las entradas de texto obligatorias no aceptan valores vacíos.
- Los identificadores inexistentes producen una respuesta controlada.
- Los formularios conservan mensajes de error comprensibles.
- Una operación no autorizada se rechaza sin ejecutar cambios.
- El nombre visible del archivo conserva el nombre original del usuario.
- El nombre utilizado en disco evita colisiones y recorridos de ruta.
