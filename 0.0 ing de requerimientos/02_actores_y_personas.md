# Actores, usuarios y personas

## 1. Actores

| Actor | Tipo | Responsabilidad | Funciones principales |
|---|---|---|---|
| Administrador | Humano, interno | Configurar y controlar el sistema | Gestionar usuarios, gestionar repositorios, consultar dashboard, cargar, buscar, descargar y eliminar documentos |
| Usuario autorizado | Humano, interno | Operar el repositorio documental | Iniciar sesión, consultar repositorios, cargar, buscar, ver y descargar documentos |
| Sistema de archivos local | Sistema externo | Conservar los archivos físicos | Recibir, entregar y retirar archivos mediante el backend |
| Base de datos SQLite | Sistema externo | Conservar datos estructurados | Guardar usuarios, repositorios, metadatos, estados y eventos |

## 2. Matriz de permisos

| Acción | Administrador | Usuario autorizado |
|---|:---:|:---:|
| Iniciar y cerrar sesión | Sí | Sí |
| Consultar dashboard | Sí | Sí |
| Crear y editar usuarios | Sí | No |
| Desactivar usuarios | Sí | No |
| Crear, editar y eliminar repositorios | Sí | No |
| Consultar repositorios | Sí | Sí |
| Cargar documentos | Sí | Sí |
| Consultar metadatos | Sí | Sí |
| Descargar documentos | Sí | Sí |
| Eliminar documentos | Sí | No |
| Consultar registro de errores | Sí | No |

## 3. Persona 1: Laura, administradora

| Atributo | Descripción |
|---|---|
| Cargo de referencia | Coordinadora administrativa |
| Experiencia digital | Media |
| Objetivos | Mantener usuarios y repositorios ordenados; revisar el volumen de archivos; resolver errores operativos |
| Necesidades | Pantallas claras, confirmación antes de eliminar, indicadores rápidos y mensajes comprensibles |
| Frustraciones | Archivos duplicados, nombres poco claros, carpetas sin responsable y errores sin explicación |
| Frecuencia de uso | Varias veces por semana |
| Dispositivo | Equipo de escritorio o portátil |

### Escenario

Laura inicia sesión, consulta el dashboard, crea un repositorio para contratos, registra un usuario y revisa si existen documentos con error. Cuando debe retirar un archivo, confirma la eliminación desde la ficha documental.

## 4. Persona 2: Carlos, usuario autorizado

| Atributo | Descripción |
|---|---|
| Cargo de referencia | Auxiliar de gestión |
| Experiencia digital | Básica a media |
| Objetivos | Cargar archivos, localizar documentos y descargarlos para su trabajo |
| Necesidades | Búsqueda simple, filtros visibles, validaciones claras y pocos pasos |
| Frustraciones | No recordar la carpeta de un archivo, formatos rechazados sin motivo y formularios extensos |
| Frecuencia de uso | Diaria |
| Dispositivo | Equipo de escritorio |

### Escenario

Carlos accede al repositorio autorizado, carga un archivo PDF y verifica que aparece en la lista. Más tarde lo localiza por una parte del nombre y lo descarga.

## 5. Necesidades de accesibilidad y facilidad de uso

- Etiquetas visibles en todos los campos.
- Navegación operable con teclado.
- Contraste suficiente entre texto y fondo.
- Mensajes que indiquen el problema y una acción posible.
- Confirmación explícita antes de una eliminación.
- Tablas adaptables a pantallas pequeñas.

## 6. Inteligencia artificial

**Pendiente de implementación.**

No se define un actor de IA ni permisos asociados en esta versión.
