"""
Qdrant Tool - Vector search with cosine similarity, filters, and threshold.

Implements vector similarity search with configurable top-k, metadata filters,
and minimum similarity threshold for Qdrant vector database.
"""
import os
import time
import asyncio
import uuid
from typing import Any, Optional
from dataclasses import dataclass

from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
    VectorParams,
    Distance,
    PointStruct,
)


@dataclass
class SearchResult:
    """Structured search result."""
    
    id: int | str
    score: float
    content: str
    metadata: dict[str, Any]
    
    @property
    def is_above_threshold(self) -> bool:
        """Check if score meets minimum threshold."""
        return self.score >= 0.7


class QdrantTool:
    """Qdrant vector search tool with filters and threshold."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection = collection or os.getenv("QDRANT_COLLECTION", "intelligence_briefs")
        
        self.score_threshold = float(os.getenv("QDRANT_SCORE_THRESHOLD", "0.7"))
        self.top_k = int(os.getenv("QDRANT_TOP_K", "10"))
        
        self.available = False
        try:
            if self.api_key:
                self.client = QdrantClient(
                    url=self.url, api_key=self.api_key,
                    port=443, https=True, prefer_grpc=False,
                )
                self.async_client = AsyncQdrantClient(
                    url=self.url, api_key=self.api_key,
                    port=443, https=True, prefer_grpc=False,
                )
            else:
                self.client = QdrantClient(
                    url=self.url,
                    port=443, https=True, prefer_grpc=False,
                )
                self.async_client = AsyncQdrantClient(
                    url=self.url,
                    port=443, https=True, prefer_grpc=False,
                )
            self.available = True
        except Exception as e:
            print(f"Qdrant not available: {e}. Running without vector DB.")
    
    def ensure_collection(self, vector_size: int = 1536) -> bool:
        """
        Create collection if it doesn't exist.
        
        Args:
            vector_size: Dimension of vectors (default 1536 for OpenAI embeddings)
            
        Returns:
            True if collection exists or was created
        """
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                return True
            return True
        except Exception as e:
            print(f"Error ensuring collection: {e}")
            return False
    
    def search(
        self,
        query_vector: list[float],
        filter_category: Optional[str] = None,
        filter_metadata: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Perform synchronous vector search with filters.
        
        Args:
            query_vector: Embedding vector for query
            filter_category: Filter by metadata.category
            filter_metadata: Additional metadata filters
            limit: Maximum results (top-k)
            score_threshold: Minimum similarity score
            
        Returns:
            List of SearchResult objects
        """
        search_limit = limit or self.top_k
        threshold = score_threshold or self.score_threshold
        
        query_filter = self._build_filter(filter_category, filter_metadata)
        
        search_params = {
            "collection_name": self.collection,
            "query": query_vector,
            "limit": search_limit,
            "score_threshold": threshold,
        }
        
        if query_filter:
            search_params["query_filter"] = query_filter
        
        results = self.client.query_points(**search_params)
        
        return self._parse_results(results)
    
    async def async_search(
        self,
        query_vector: list[float],
        filter_category: Optional[str] = None,
        filter_metadata: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Perform asynchronous vector search with filters.
        
        Args:
            query_vector: Embedding vector for query
            filter_category: Filter by metadata.category
            filter_metadata: Additional metadata filters
            limit: Maximum results (top-k)
            score_threshold: Minimum similarity score
            
        Returns:
            List of SearchResult objects
        """
        search_limit = limit or self.top_k
        threshold = score_threshold or self.score_threshold
        
        query_filter = self._build_filter(filter_category, filter_metadata)
        
        search_params = {
            "collection_name": self.collection,
            "query": query_vector,
            "limit": search_limit,
            "score_threshold": threshold,
        }
        
        if query_filter:
            search_params["query_filter"] = query_filter
        
        results = await self.async_client.query_points(**search_params)
        
        return self._parse_results(results)
    
    def search_by_text(
        self,
        text: str,
        embedding_func: Any,
        filter_category: Optional[str] = None,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Search using text with external embedding function.
        
        Args:
            text: Query text
            embedding_func: Function that converts text to embedding vector
            filter_category: Filter by metadata.category
            limit: Maximum results
            score_threshold: Minimum similarity score
            
        Returns:
            List of SearchResult objects
        """
        query_vector = embedding_func(text)
        return self.search(
            query_vector=query_vector,
            filter_category=filter_category,
            limit=limit,
            score_threshold=score_threshold,
        )
    
    def upsert(
        self,
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        ids: Optional[list[int | str]] = None,
    ) -> bool:
        """
        Insert or update vectors with payloads.
        
        Args:
            vectors: List of embedding vectors
            payloads: List of metadata payloads
            ids: Optional list of point IDs
            
        Returns:
            True if successful
        """
        if ids is None:
            ids = list(range(len(vectors)))
        
        points = [
            PointStruct(id=idx, vector=vec, payload=payload)
            for idx, vec, payload in zip(ids, vectors, payloads)
        ]
        
        try:
            self.client.upsert(
                collection_name=self.collection,
                points=points,
            )
            return True
        except Exception as e:
            print(f"Upsert error: {e}")
            return False
    
    def _build_filter(
        self,
        filter_category: Optional[str] = None,
        filter_metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[Filter]:
        """Build Qdrant filter from parameters."""
        conditions = []
        
        if filter_category:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=filter_category),
                )
            )
        
        if filter_metadata:
            for key, value in filter_metadata.items():
                conditions.append(
                    FieldCondition(
                        key=f"metadata.{key}",
                        match=MatchValue(value=value),
                    )
                )
        
        if not conditions:
            return None
        
        return Filter(must=conditions)
    
    def _parse_results(self, results: Any) -> list[SearchResult]:
        """Parse Qdrant results into SearchResult objects."""
        parsed = []
        
        for point in results.points:
            payload = point.payload or {}
            result = SearchResult(
                id=point.id,
                score=point.score,
                content=payload.get("content", ""),
                metadata={
                    "category": payload.get("category", ""),
                    "source": payload.get("source", ""),
                    "date": payload.get("date", ""),
                    "url": payload.get("url", ""),
                    **payload.get("metadata", {}),
                },
            )
            parsed.append(result)
        
        return parsed
    
    def get_collection_info(self) -> dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.collection)
            return {
                "name": self.collection,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_points(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get all stored points with their payloads."""
        try:
            points, _ = self.client.scroll(
                collection_name=self.collection,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            
            results = []
            for point in points:
                payload = point.payload or {}
                results.append({
                    "id": str(point.id),
                    "content": payload.get("content", "")[:500],
                    "category": payload.get("category", ""),
                    "source": payload.get("source", ""),
                    "type": payload.get("type", ""),
                    "query": payload.get("query", ""),
                    "date": payload.get("date", ""),
                    "url": payload.get("url", ""),
                    "title": payload.get("title", ""),
                })
            
            return results
        except Exception as e:
            print(f"Error getting points: {e}")
            return []
    
    def search_by_text_local(
        self,
        text: str,
        embedding_func: Any,
        limit: int = 5,
        score_threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Search Qdrant by text using provided embedding function."""
        try:
            import asyncio
            embedding = asyncio.run(embedding_func(text))
            
            results = self.client.query_points(
                collection_name=self.collection,
                query=embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            
            parsed = []
            for point in results.points:
                payload = point.payload or {}
                parsed.append({
                    "id": str(point.id),
                    "score": point.score,
                    "content": payload.get("content", "")[:800],
                    "category": payload.get("category", ""),
                    "source": payload.get("source", ""),
                    "query": payload.get("query", ""),
                    "date": payload.get("date", ""),
                    "type": payload.get("type", ""),
                })
            
            return parsed
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def store_research(
        self,
        query: str,
        brief: str,
        sources: list[dict[str, Any]],
        dimensions: list[dict[str, Any]],
        embedding_func: Any,
    ) -> bool:
        """
        Store research results for future context.
        
        Saves the brief and sources as separate vectors so future queries
        can find relevant past research.
        """
        stored = 0
        
        # Store the full brief
        brief_embedding = await embedding_func(query + " " + brief[:500])
        brief_payload = {
            "content": brief,
            "category": "brief",
            "source": "pipeline",
            "query": query,
            "date": time.strftime("%Y-%m-%d"),
            "dimensions": [d["name"] for d in dimensions],
            "type": "research_brief",
        }
        
        if self.upsert(
            vectors=[brief_embedding],
            payloads=[brief_payload],
            ids=[str(uuid.uuid4())],
        ):
            stored += 1
        
        # Store top sources individually
        for i, source in enumerate(sources[:10]):
            if not source.get("content"):
                continue
            
            source_embedding = await embedding_func(source["content"][:500])
            source_payload = {
                "content": source["content"][:1000],
                "category": source.get("dimension", "general"),
                "source": source.get("source", "web"),
                "url": source.get("url", ""),
                "title": source.get("title", ""),
                "score": source.get("score", 0),
                "date": time.strftime("%Y-%m-%d"),
                "type": "research_source",
            }
            
            if self.upsert(
                vectors=[source_embedding],
                payloads=[source_payload],
                ids=[str(uuid.uuid4())],
            ):
                stored += 1
        
        print(f"  [QDRANT] Stored {stored} items for query: {query[:50]}")
        return stored > 0