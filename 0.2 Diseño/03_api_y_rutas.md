# Rutas web diseñadas

| Método | Ruta | Uso |
|---|---|---|
| GET/POST | `/registro` | Crear cuenta. |
| GET/POST | `/login` | Iniciar sesión. |
| POST | `/logout` | Cerrar sesión. |
| GET | `/dashboard` | Métricas y actividad. |
| GET | `/repositorios` | Listar repositorios. |
| GET/POST | `/repositorios/nuevo` | Crear repositorio. |
| GET | `/repositorios/<id>` | Ver documentos. |
| POST | `/repositorios/<id>/documentos` | Cargar PDF, DOCX o TXT. |
| GET | `/buscar?q=...` | Buscar metadatos. |
| GET | `/documentos/<id>/descargar` | Descargar con autorización. |
| POST | `/documentos/<id>/eliminar` | Eliminar documento. |
| GET | `/ia` | Mostrar estado de IA pendiente. |

