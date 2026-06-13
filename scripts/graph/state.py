"""
LangGraph State - TypedDict definitions for workflow state.
"""
from typing import TypedDict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Dimension:
    """Analysis dimension."""
    name: str
    description: str
    priority: str  # high, medium, low
    sources_required: int = 3


@dataclass
class SearchResult:
    """Search result from Tavily or Qdrant."""
    title: str
    url: str
    content: str
    score: float
    source: str  # tavily or qdrant
    published_date: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CritiqueResult:
    """Result from self-critique loop."""
    strengths: list[str]
    weaknesses: list[str]
    gaps: list[str]
    biases: list[str]
    redundancies: list[str]
    suggestions: list[str]
    score: float
    should_continue: bool


class AgentState(TypedDict):
    """Main state for the intelligence brief pipeline."""
    query: str
    analysis_dimensions: list[dict[str, Any]]
    tavily_results: list[dict[str, Any]]
    qdrant_context: list[dict[str, Any]]
    synthesized_brief: str
    loop_iteration: int
    quality_score: float
    is_complete: bool
    critique: Optional[dict[str, Any]]
    metadata: dict[str, Any]


def create_initial_state(query: str) -> AgentState:
    """
    Create initial state for the pipeline.
    
    Args:
        query: User's research query
        
    Returns:
        Initial AgentState
    """
    return {
        "query": query,
        "analysis_dimensions": [],
        "tavily_results": [],
        "qdrant_context": [],
        "synthesized_brief": "",
        "loop_iteration": 0,
        "quality_score": 0.0,
        "is_complete": False,
        "critique": None,
        "metadata": {
            "start_time": None,
            "end_time": None,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
        },
    }