# PRD: Intelligence Brief Generator

## Visión del Producto

Generar Intelligence Briefs estratégicos que combinen noticias recientes de la web con contexto histórico para提供 análisis de alta calidad con nivel de analista senior.

## Objetivos

1. **Automatizar** la investigación de inteligencia competitiva
2. **Combinar** fuentes en tiempo real con conocimiento histórico
3. **Garantizar** calidad mediante loop de mejora iterativa
4. **Reducir** tiempo de análisis de horas a minutos

## Usuarios Target

- Analistas de inteligencia competitiva
- Equipos de estrategia empresarial
- Consultores de negocio
- Investidores y fondos de capital

## Funcionalidades

### F1: Descomposición de Queries
- Recibir query del usuario
- Identificar dimensiones de análisis
- Definir criterios de aceptación

### F2: Investigación Paralela
- Búsqueda Tavily (noticias 72h)
- Recuperación Qdrant (contexto histórico)
- Filtros por relevancia y fecha

### F3: Síntesis Inteligente
- Combinación de fuentes
- Eliminación de redundancias
- Separación hechos/interpretación

### F4: Loop Engineering
- Auto-crítica del borrador
- Investigación dirigida de gaps
- Refinamiento iterativo (max 5 loops)

### F5: Validación QA
- Verificación de fuentes
- Score de calidad (min 8/10)
- Detección de sesgos

## Métricas de Éxito

| Métrica | Target |
|---------|--------|
| Tiempo de generación | < 3 min |
| Score de calidad | ≥ 8/10 |
| Fuentes verificadas | ≥ 3 por dimensión |
| Costo por reporte | ≤ $0.10 USD |

## Restricciones

- Rate limit Tavily: 1000 requests/mes
- Timeout total: 3 minutos
- Max iteraciones loop: 5
- Costo OpenRouter: $0.10 max

## Cronograma

| Fase | Duración | Entregable |
|------|----------|------------|
| Setup | 1 semana | Infraestructura |
| MVP | 2 semanas | Pipeline básico |
| Loop Eng | 1 semana | Iteración automática |
| QA | 1 semana | Validación completa |
| Total | 5 semanas | v1.0 production