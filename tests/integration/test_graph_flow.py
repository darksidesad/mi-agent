"""
Integration tests for LangGraph workflow.
"""
import pytest
from unittest.mock import patch, MagicMock
from scripts.graph.workflow import create_workflow
from scripts.graph.state import AgentState, create_initial_state


MOCK_ENV = {
    "TAVILY_API_KEY": "test-tavily-key",
    "OPENROUTER_API_KEY": "test-openrouter-key",
    "QDRANT_URL": "http://localhost:6333",
    "QDRANT_API_KEY": "test-qdrant-key",
}


class TestWorkflow:
    """Tests for LangGraph workflow."""
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_workflow_initializes(self):
        workflow = create_workflow()
        assert workflow is not None
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_workflow_has_nodes(self):
        workflow = create_workflow()
        graph = workflow.get_graph()
        
        node_names = list(graph.nodes.keys())
        
        assert "decompose_query" in node_names
        assert "research_parallel" in node_names
        assert "synthesize" in node_names
        assert "self_critique" in node_names
        assert "refine" in node_names
        assert "validate" in node_names
        assert "deliver" in node_names


class TestAgentState:
    """Tests for AgentState."""
    
    def test_create_initial_state(self):
        state = create_initial_state("test query")
        
        assert state["query"] == "test query"
        assert state["analysis_dimensions"] == []
        assert state["tavily_results"] == []
        assert state["qdrant_context"] == []
        assert state["synthesized_brief"] == ""
        assert state["loop_iteration"] == 0
        assert state["quality_score"] == 0.0
        assert state["is_complete"] is False
        assert state["critique"] is None
        assert "metadata" in state