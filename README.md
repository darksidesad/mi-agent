# Intelligence Brief Generator

Sistema de agentes para generar Intelligence Briefs estratégicos combinando noticias recientes con contexto histórico.

## Componentes

- **LangGraph**: Orquestación de agentes
- **Tavily API**: Búsqueda web en tiempo real
- **Qdrant**: Memoria a largo plazo
- **OpenRouter**: LLMs multi-modelo

## Quick Start

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar pipeline
python scripts/main.py
```

## Docker

```bash
docker-compose up
```

## Estructura

```
intelligence-brief-agent/
├── .opencode/
│   ├── agents/          # Agentes definidos
│   └── skills/          # Skills personalizados
├── docs/                # Documentación
├── scripts/             # Código Python
│   ├── agents/          # Lógica de agentes
│   ├── tools/           # Wrappers de APIs
│   ├── graph/           # LangGraph workflow
│   └── loops/           # Loop engineering
└── tests/               # Tests
```

## Agentes

| Agente | Rol |
|--------|-----|
| Orchestrator | Controlador principal |
| Product Owner | Descompone queries |
| Architect | Diseña el pipeline |
| Developer | Implementa código |
| DevOps | Infraestructura |
| QA | Validación |

## Licencia

MIT