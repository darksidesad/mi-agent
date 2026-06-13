"""
Unit tests for Tavily Tool.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scripts.tools.tavily_tool import TavilyTool, RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""
    
    def test_can_request_within_limit(self):
        limiter = RateLimiter()
        assert limiter.can_request() is True
    
    def test_records_request(self):
        limiter = RateLimiter()
        limiter.record_request()
        assert limiter.current_count == 1
    
    def test_get_remaining(self):
        limiter = RateLimiter()
        limiter.record_request()
        assert limiter.get_remaining() == 999


class TestTavilyTool:
    """Tests for TavilyTool class."""
    
    @pytest.fixture
    def mock_tavily(self):
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            tool = TavilyTool()
            tool.client = MagicMock()
            tool.async_client = MagicMock()
            return tool
    
    def test_init_with_env(self):
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            tool = TavilyTool()
            assert tool.api_key == "test-key"
    
    def test_init_without_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError):
                TavilyTool()
    
    def test_extract_metadata(self, mock_tavily):
        raw_response = {
            "query": "test query",
            "answer": "Test answer",
            "results": [
                {
                    "title": "Test Title",
                    "url": "https://example.com",
                    "content": "Test content",
                    "score": 0.95,
                    "published_date": "2026-06-10",
                }
            ],
            "total_results": 1,
            "response_time": 0.5,
        }
        
        result = mock_tavily._extract_metadata(raw_response)
        
        assert result["query"] == "test query"
        assert result["has_answer"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Title"
        assert result["results"][0]["domain"] == "example.com"
        assert result["results"][0]["relevance_tier"] == "high"
    
    def test_extract_domain(self, mock_tavily):
        assert mock_tavily._extract_domain("https://example.com/path") == "example.com"
        assert mock_tavily._extract_domain("https://sub.example.com") == "sub.example.com"
        assert mock_tavily._extract_domain("") == ""
    
    def test_get_relevance_tier(self, mock_tavily):
        assert mock_tavily._get_relevance_tier(0.95) == "high"
        assert mock_tavily._get_relevance_tier(0.75) == "medium"
        assert mock_tavily._get_relevance_tier(0.55) == "low"
        assert mock_tavily._get_relevance_tier(0.3) == "very_low"
    
    def test_rate_limit_info(self, mock_tavily):
        info = mock_tavily.get_rate_limit_info()
        assert "remaining" in info
        assert "max" in info
        assert "used" in info