"""
Unit tests for Qdrant Tool.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from scripts.tools.qdrant_tool import QdrantTool, SearchResult


class TestSearchResult:
    """Tests for SearchResult class."""
    
    def test_above_threshold(self):
        result = SearchResult(
            id=1,
            score=0.85,
            content="test",
            metadata={},
        )
        assert result.is_above_threshold is True
    
    def test_below_threshold(self):
        result = SearchResult(
            id=1,
            score=0.5,
            content="test",
            metadata={},
        )
        assert result.is_above_threshold is False


class TestQdrantTool:
    """Tests for QdrantTool class."""
    
    @pytest.fixture
    def mock_qdrant(self):
        with patch.dict("os.environ", {
            "QDRANT_URL": "http://localhost:6333",
            "QDRANT_API_KEY": "test-key",
            "QDRANT_COLLECTION": "test_collection",
        }):
            tool = QdrantTool()
            tool.client = MagicMock()
            tool.async_client = MagicMock()
            return tool
    
    def test_init_with_env(self):
        with patch.dict("os.environ", {
            "QDRANT_URL": "http://test:6333",
            "QDRANT_API_KEY": "test-key",
        }):
            tool = QdrantTool()
            assert tool.url == "http://test:6333"
            assert tool.api_key == "test-key"
    
    def test_build_filter_category(self, mock_qdrant):
        filter_obj = mock_qdrant._build_filter(filter_category="fintech")
        assert filter_obj is not None
        assert len(filter_obj.must) == 1
    
    def test_build_filter_metadata(self, mock_qdrant):
        filter_obj = mock_qdrant._build_filter(
            filter_metadata={"source": "web", "year": "2026"}
        )
        assert filter_obj is not None
        assert len(filter_obj.must) == 2
    
    def test_build_filter_empty(self, mock_qdrant):
        filter_obj = mock_qdrant._build_filter()
        assert filter_obj is None
    
    def test_parse_results(self, mock_qdrant):
        mock_point = MagicMock()
        mock_point.id = 1
        mock_point.score = 0.85
        mock_point.payload = {
            "content": "test content",
            "category": "fintech",
            "source": "web",
        }
        
        mock_results = MagicMock()
        mock_results.points = [mock_point]
        
        parsed = mock_qdrant._parse_results(mock_results)
        
        assert len(parsed) == 1
        assert parsed[0].id == 1
        assert parsed[0].score == 0.85
        assert parsed[0].content == "test content"
    
    def test_collection_info(self, mock_qdrant):
        mock_info = MagicMock()
        mock_info.vectors_count = 100
        mock_info.points_count = 50
        mock_info.status = "green"
        mock_qdrant.client.get_collection.return_value = mock_info
        
        info = mock_qdrant.get_collection_info()
        
        assert info["vectors_count"] == 100
        assert info["points_count"] == 50
        assert info["status"] == "green"