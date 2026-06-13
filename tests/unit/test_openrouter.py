"""
Unit tests for OpenRouter Tool.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scripts.tools.openrouter_tool import OpenRouterTool, TokenUsage, ModelTier, MODELS


class TestOpenRouterTool:
    """Tests for OpenRouterTool class."""
    
    @pytest.fixture
    def mock_openrouter(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
            tool = OpenRouterTool()
            return tool
    
    def test_init_with_env(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
            tool = OpenRouterTool()
            assert tool.api_key == "test-key"
    
    def test_init_without_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError):
                OpenRouterTool()
    
    def test_models_config(self):
        assert "openai/gpt-4o-mini" in MODELS
        assert "anthropic/claude-sonnet-4-20250514" in MODELS
        
        fast_model = MODELS["openai/gpt-4o-mini"]
        assert fast_model.tier == ModelTier.FAST
        
        reasoning_model = MODELS["anthropic/claude-sonnet-4-20250514"]
        assert reasoning_model.tier == ModelTier.REASONING
    
    def test_calculate_cost(self, mock_openrouter):
        cost = mock_openrouter._calculate_cost(
            "openai/gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        
        expected_input = (1000 / 1000) * 0.00015
        expected_output = (500 / 1000) * 0.0006
        expected = expected_input + expected_output
        
        assert abs(cost - expected) < 0.0001
    
    def test_usage_stats(self, mock_openrouter):
        stats = mock_openrouter.get_usage_stats()
        
        assert "prompt_tokens" in stats
        assert "completion_tokens" in stats
        assert "total_tokens" in stats
        assert "cost_usd" in stats
        assert "remaining_budget" in stats


class TestTokenUsage:
    """Tests for TokenUsage class."""
    
    def test_default_values(self):
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0
        assert usage.cost_usd == 0.0