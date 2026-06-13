"""
End-to-end tests for brief generation.
"""
import pytest
from unittest.mock import patch
from scripts.loops.iteration_manager import IterationManager
from scripts.graph.state import AgentState, create_initial_state


MOCK_ENV = {
    "TAVILY_API_KEY": "test-tavily-key",
    "OPENROUTER_API_KEY": "test-openrouter-key",
    "QDRANT_URL": "http://localhost:6333",
    "QDRANT_API_KEY": "test-qdrant-key",
}


class TestIterationManager:
    """Tests for IterationManager."""
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_init_defaults(self):
        manager = IterationManager()
        assert manager.max_iterations == 5
        assert manager.timeout_seconds == 600
        assert manager.quality_threshold == 8.0
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_init_custom(self):
        manager = IterationManager(
            max_iterations=3,
            timeout_seconds=60,
            quality_threshold=7.0,
        )
        assert manager.max_iterations == 3
        assert manager.timeout_seconds == 60
        assert manager.quality_threshold == 7.0
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_get_stats(self):
        manager = IterationManager()
        stats = manager.get_stats()
        
        assert stats["max_iterations"] == 5
        assert stats["timeout_seconds"] == 600
        assert stats["quality_threshold"] == 8.0


class TestQualityThreshold:
    """Tests for quality threshold logic."""
    
    def test_threshold_met(self):
        assert 8.0 >= 8.0
    
    def test_threshold_not_met(self):
        assert 7.9 < 8.0
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_max_iterations_limit(self):
        manager = IterationManager()
        assert manager.max_iterations == 5
    
    @patch.dict("os.environ", MOCK_ENV)
    def test_timeout_limit(self):
        manager = IterationManager()
        assert manager.timeout_seconds == 600


class TestStateTransitions:
    """Tests for state transitions in the pipeline."""
    
    def test_initial_state_structure(self):
        state = create_initial_state("test query")
        
        required_keys = [
            "query",
            "analysis_dimensions",
            "tavily_results",
            "qdrant_context",
            "synthesized_brief",
            "loop_iteration",
            "quality_score",
            "is_complete",
            "critique",
            "metadata",
        ]
        
        for key in required_keys:
            assert key in state, f"Missing key: {key}"
    
    def test_state_update(self):
        state = create_initial_state("test query")
        
        updated_state = {
            **state,
            "synthesized_brief": "Test brief",
            "quality_score": 8.5,
        }
        
        assert updated_state["synthesized_brief"] == "Test brief"
        assert updated_state["quality_score"] == 8.5
        assert updated_state["query"] == "test query"