"""Punto de extensión para la futura integración con inteligencia artificial.

Este archivo no realiza llamadas externas, no importa SDK de IA y no utiliza
credenciales. Se conserva como estructura para una iteración futura.
"""


def estado_integracion() -> dict[str, str]:
    """Informa el estado actual sin procesar ningún documento."""
    return {
        "estado": "Pendiente de implementación",
        "clasificacion": "Pendiente de implementación",
        "resumen": "Pendiente de implementación",
        "extraccion": "Pendiente de implementación",
        "preguntas": "Pendiente de implementación",
    }
