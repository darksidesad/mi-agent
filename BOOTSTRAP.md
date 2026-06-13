# BOOTSTRAP + LOOP ENGINEERING

Cuando recibas un nuevo proyecto, ejecuta este flujo:

## FASE 1: CREACIÓN (Harness Engineering)

### PASO 1: Product Owner Agent
Lee el brief del usuario y genera:
- `docs/PRD.md` (Product Requirements Document)
- `docs/DOD.md` (Definition of Done)
- `AGENTS.md` (índice central del proyecto)

### PASO 2: Architect Agent
Diseña la arquitectura y genera:
- `docs/architecture.md`
- `.opencode/agents/*.md` (todos los agentes)
- `.opencode/skills/*/SKILL.md` (skills reutilizables)
- Estructura de carpetas del proyecto

### PASO 3: Developer Agent
Implementa el código:
- Crea estructura de carpetas
- Implementa cada archivo con código funcional
- `requirements.txt` con versiones exactas
- `.env.example` con variables necesarias

### PASO 4: DevOps Agent
Configura infraestructura:
- `.gitignore`, `Dockerfile`, `docker-compose.yml`
- Variables de entorno por ambiente

### PASO 5: QA Agent
Crea tests y valida:
- `tests/unit/`, `tests/integration/`, `tests/e2e/`
- Ejecuta pytest y verifica que pasen

---

## FASE 2: MEJORA ITERATIVA (Loop Engineering)

Después de la creación inicial, aplica este loop HASTA que el proyecto esté completo:

### LOOP 1: Generación Inicial
- Revisa todo el código generado
- Identifica qué falta, qué está incompleto
- Lista de tareas pendientes

### LOOP 2: Crítica Interna
Pregúntate como QA Agent:
- ¿Qué archivos tienen código incompleto o placeholder?
- ¿Qué funcionalidades no están implementadas?
- ¿Hay imports rotos o dependencias faltantes?
- ¿Los tests cubren los casos principales?
- ¿La documentación refleja el código real?

Genera: `docs/critique_v1.md` con la lista de problemas encontrados

### LOOP 3: Investigación Dirigida
- Lee cada archivo del proyecto
- Identifica gaps específicos
- Consulta documentación de las tecnologías usadas
- Busca mejores prácticas para cada componente

### LOOP 4: Refinamiento
Implementa TODAS las correcciones encontradas:
- Completa código faltante
- Arregla imports y dependencias
- Agrega tests faltantes
- Actualiza documentación
- Agrega manejo de errores
- Implementa validación de inputs

### LOOP 5: Validación Final
- Ejecuta `pytest` completo
- Verifica que no hay errores de sintaxis
- Confirma que la estructura está completa
- Revisa que `.env.example` tiene todas las variables
- Confirma que `Dockerfile` y `docker-compose.yml` funcionan

**Si hay errores → volver al LOOP 2**
**Si todo pasa → ENTREGAR**

---

## REGLAS GENERALES

- Cada agente solo genera archivos de su responsabilidad
- Todo código debe ser copy-paste ejecutable (no pseudocódigo)
- Máximo 5 iteraciones de loop engineering
- Si después de 5 loops hay errores críticos, reportar al usuario
- Cada loop debe ser documentado en `docs/loop_history.md`

## FORMATO DE ENTREGA

Al terminar, entrega:
1. Estructura completa de archivos
2. `docs/loop_history.md` (resumen de cada iteración)
3. Instrucciones de ejecución
4. Estado final: TODOs pendientes (si los hay)
