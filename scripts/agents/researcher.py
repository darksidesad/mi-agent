"""
Researcher Agent - Handles Tavily and Qdrant searches.
"""
import asyncio
from typing import Any, Optional

from scripts.tools.tavily_tool import TavilyTool
from scripts.tools.qdrant_tool import QdrantTool
from scripts.tools.openrouter_tool import OpenRouterTool


class ResearcherAgent:
    """Research agent that combines web search and vector database."""
    
    def __init__(self):
        self.tavily = TavilyTool()
        self.qdrant = QdrantTool()
        self.llm = OpenRouterTool()
    
    async def search_tavily(
        self,
        query: str,
        dimensions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Search Tavily for recent news and information.
        
        Args:
            query: Research query
            dimensions: Analysis dimensions
            
        Returns:
            List of search results
        """
        all_results = []
        
        for dimension in dimensions:
            dim_query = f"{query} {dimension['name'].replace('_', ' ')}"
            
            try:
                result = await self.tavily.async_search(
                    query=dim_query,
                    search_depth="advanced",
                    max_results=5,
                    days=3,
                    topic="general",
                    include_answer=True,
                )
                
                for item in result.get("results", []):
                    item["dimension"] = dimension["name"]
                    item["source"] = "tavily"
                
                all_results.extend(result.get("results", []))
                
            except Exception as e:
                print(f"Tavily search error for {dimension['name']}: {e}")
                continue
        
        return self._deduplicate_results(all_results)
    
    async def search_qdrant(
        self,
        query: str,
        dimensions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Search Qdrant for historical context.
        
        Args:
            query: Research query
            dimensions: Analysis dimensions
            
        Returns:
            List of context items
        """
        all_context = []
        
        embedding = await self.llm.get_embedding(query)
        
        for dimension in dimensions:
            try:
                results = await self.qdrant.async_search(
                    query_vector=embedding,
                    filter_category=dimension["name"],
                    limit=5,
                    score_threshold=0.7,
                )
                
                for result in results:
                    all_context.append({
                        "content": result.content,
                        "score": result.score,
                        "category": result.metadata.get("category", ""),
                        "source": "qdrant",
                        "metadata": result.metadata,
                    })
                
            except Exception as e:
                print(f"Qdrant search error for {dimension['name']}: {e}")
                continue
        
        return all_context
    
    def _deduplicate_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results