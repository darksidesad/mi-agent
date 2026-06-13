# Loop Engineering

## Concepto

Loop Engineering es un proceso de mejora iterativa que refina automáticamente los reportes de inteligencia hasta alcanzar calidad aceptable.

## Flujo del Loop

```
┌─────────────────────────────────────────────────────────┐
│                    LOOP ENGINEERING                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐                                        │
│  │  LOOP 1     │  Generación inicial (v0)               │
│  │  Generate   │  - Todas las fuentes disponibles       │
│  └─────────────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │  LOOP 2     │  Crítica interna                       │
│  │  Critique   │  - Gaps identificados                  │
│  │             │  - Sesgos detectados                   │
│  │             │  - Redundancias marcadas               │
│  └─────────────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │  LOOP 3     │  Investigación dirigida                │
│  │  Research   │  - Búsqueda específica de gaps         │
│  │             │  - Fuentes opuestas                    │
│  │             │  - Contexto complementario             │
│  └─────────────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │  LOOP 4     │  Refinamiento                          │
│  │  Refine     │  - Integrar nuevo material             │
│  │             │  - Reescribir secciones débiles        │
│  │             │  - Agregar matices                      │
│  └─────────────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐     score < 8    ┌─────────────┐      │
│  │  LOOP 5     │ ───────────────► │  Volver a   │      │
│  │  Validate   │                  │  LOOP 2     │      │
│  │             │                  └─────────────┘      │
│  │  Score ≥ 8  │                                        │
│  └─────────────┘                                        │
│         │                                               │
│         ▼                                               │
│  ┌─────────────┐                                        │
│  │  ENTREGAR   │  Reporte final                         │
│  └─────────────┘                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Límites del Sistema

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Max iteraciones | 5 | Evitar loop infinito |
| Timeout total | 3 min | UX y costo |
| Costo máximo | $0.10 | Presupuesto por reporte |
| Score mínimo | 8/10 | Calidad aceptable |

## Preguntas de Crítica (LOOP 2)

1. ¿Qué información falta en este reporte?
2. ¿Estoy favoreciendo alguna perspectiva?
3. ¿Hay contradicciones entre fuentes?
4. ¿Las proyecciones están respaldadas?
5. ¿El nivel técnico es adecuado?

## Estrategias de Investigación Dirigida (LOOP 3)

- **Gaps de información**: Buscar fuentes específicas sobre temas faltantes
- **Balance de perspectivas**: Consultar fuentes con opiniones opuestas
- **Contexto histórico**: Ampliar Qdrant con datos complementarios
- **Verificación**: Confirmar claims dudosos con fuentes adicionales