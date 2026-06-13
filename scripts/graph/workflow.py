"""
LangGraph Workflow - Main pipeline graph with parallel research.
"""
import asyncio
from typing import Any, Optional
from langgraph.graph import StateGraph, END, START

from scripts.graph.state import AgentState, create_initial_state
from scripts.agents.orchestrator import OrchestratorAgent


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for intelligence brief generation.
    
    Pipeline:
    1. decompose_query - Product Owner identifies dimensions
    2. research_parallel - Tavily + Qdrant in parallel
    3. synthesize - Combine sources
    4. self_critique - Loop engineering core
    5. refine - Improve based on critique
    6. validate - QA Agent checks quality
    7. deliver - Final output
    """
    orchestrator = OrchestratorAgent()
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("decompose_query", orchestrator.decompose_query)
    workflow.add_node("research_parallel", orchestrator.research_parallel)
    workflow.add_node("synthesize", orchestrator.synthesize)
    workflow.add_node("self_critique", orchestrator.self_critique)
    workflow.add_node("refine", orchestrator.refine)
    workflow.add_node("validate", orchestrator.validate)
    workflow.add_node("deliver", orchestrator.deliver)
    
    workflow.add_edge(START, "decompose_query")
    workflow.add_edge("decompose_query", "research_parallel")
    workflow.add_edge("research_parallel", "synthesize")
    workflow.add_edge("synthesize", "self_critique")
    workflow.add_edge("self_critique", "refine")
    workflow.add_edge("refine", "validate")
    
    workflow.add_conditional_edges(
        "validate",
        orchestrator.should_continue,
        {
            "continue": "self_critique",
            "complete": "deliver",
        },
    )
    
    workflow.add_edge("deliver", END)
    
    return workflow.compile()


async def run_pipeline(query: str) -> AgentState:
    """
    Run the complete intelligence brief pipeline.
    
    Args:
        query: User's research query
        
    Returns:
        Final AgentState with complete brief
    """
    workflow = create_workflow()
    initial_state = create_initial_state(query)
    
    result = await workflow.ainvoke(initial_state)
    
    return result