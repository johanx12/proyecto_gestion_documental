# Registro de defectos

No se reportan defectos confirmados porque en esta entrega no se afirma una ejecución. La tabla siguiente contiene riesgos que el equipo debe comprobar; su estado es `Por validar` y no debe interpretarse como fallo observado.

## Escala

| Severidad | Definición |
|---|---|
| Crítica | Expone documentos, pierde datos o impide iniciar el sistema. |
| Alta | Bloquea una función principal sin alternativa razonable. |
| Media | Afecta una función secundaria o tiene alternativa temporal. |
| Baja | Afecta texto, estilo o comodidad sin impedir el flujo. |

## Riesgos por validar

| ID | Riesgo a comprobar | Severidad potencial | Caso relacionado | Estado |
|---|---|---:|---|---|
| RV-01 | Acceso a una descarga cambiando el identificador de URL | Crítica | CP-11 | Por validar |
| RV-02 | Archivo físico creado aunque falle el registro en BD | Alta | CP-06 | Por validar |
| RV-03 | Nombre original con ruta o caracteres especiales | Alta | CP-05, CP-07 | Por validar |
| RV-04 | Usuario común accede al reporte global | Alta | CP-04, CP-14 | Por validar |
| RV-05 | Documento archivado continúa en búsqueda normal | Media | CP-08, CP-13 | Por validar |
| RV-06 | Reporte cuenta registros fuera del intervalo | Media | CP-14 | Por validar |
| RV-07 | Aplicación intenta usar IA sin configuración | Media | CP-15 | Por validar |

## Plantilla de defecto confirmado

```text
ID:
Título:
Fecha:
Reportado por:
Versión o commit:
Ambiente:
Severidad: Crítica | Alta | Media | Baja
Prioridad: Urgente | Alta | Normal | Baja
Precondiciones:
Pasos para reproducir:
Resultado observado:
Resultado esperado:
Evidencia:
Estado:
Responsable de corrección:
Notas de repetición:
```

Antes de cerrar un defecto se debe repetir el caso que lo detectó y al menos un caso relacionado para reducir regresiones.
