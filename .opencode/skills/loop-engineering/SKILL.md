---
name: loop-engineering
description: Aplica loop de mejora iterativa para refinar reportes de inteligencia. Usa cuando se necesite iterar y mejorar un borrador hasta alcanzar calidad aceptable.
---

# LOOP_ENGINEERING_PROMPT = """
APLICA EL SIGUIENTE LOOP DE MEJORA ITERATIVA:

LOOP 1 - GENERACIÓN INICIAL:
- Generar borrador v0 con todas las fuentes

LOOP 2 - CRÍTICA INTERNA (Self-Critique):
Preguntar: "¿Qué debilidades tiene este reporte v0?"
- Identificar gaps: información faltante, fuentes débiles
- Identificar sesgos: ¿estoy favoreciendo una perspectiva?
- Identificar redundancias

LOOP 3 - INVESTIGACIÓN DIRIGIDA:
- Buscar específicamente lo que faltaba
- Consultar fuentes opuestas para balance
- Ampliar Qdrant con contexto complementario

LOOP 4 - REFINAMIENTO:
- Integrar nuevo material
- Reescribir secciones débiles
- Agregar matices y contra-argumentos

LOOP 5 - VALIDACIÓN FINAL:
- QA Agent valida el reporte v5
- Si score < 8/10 → volver a LOOP 2
- Si score >= 8/10 → entregar

LÍMITES DEL LOOP:
- Máximo 5 iteraciones (evitar loop infinito)
- Timeout total: 3 minutos por query
- Costo máximo estimado: $0.10 en OpenRouter por reporte
"""