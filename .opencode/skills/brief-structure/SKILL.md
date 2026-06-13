---
name: brief-structure
description: Template para la estructura del Intelligence Brief final. Usa cuando se vaya a generar o validar el reporte final.
---

# Brief Structure Template

## Estructura del Reporte

```markdown
# Intelligence Brief: [TÍTULO]
**Fecha:** [YYYY-MM-DD]
**Query:** [query original]
**Analista:** Orchestrator Agent v1.0

## Executive Summary
[2-3 párrafos con los hallazgos principales]

## Análisis por Dimensión

### 1. [Dimensión 1]
**Fuentes:** [lista de URLs]
**Hallazgos:** [análisis detallado]
**Confianza:** [alta|media|baja]

### 2. [Dimensión 2]
**Fuentes:** [lista de URLs]
**Hallazgos:** [análisis detallado]
**Confianza:** [alta|media|baja]

### N. [Dimensión N]
...

## Contexto Histórico
[Referencia a datos previos en Qdrant]

## Proyecciones
[Tendencias y escenarios futuros]

## Metodología
- Fuentes consultadas: [número]
- Período cubierto: [rango de fechas]
- Profundidad de búsqueda: [basic|advanced]
- Iteraciones de mejora: [número]

## Anexo: Fuentes Completas
| # | Fuente | URL | Fecha | Relevancia |
|---|--------|-----|-------|------------|
| 1 | ... | ... | ... | ... |
```

## Criterios de Calidad
- [ ] Executive summary en max 300 palabras
- [ ] Cada dimensión tiene min 3 fuentes
- [ ] URLs verificadas y accesibles
- [ ] Separación clara: hechos vs interpretación
- [ ] Proyecciones basadas en evidencia