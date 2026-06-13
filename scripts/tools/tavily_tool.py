"""
Tavily Tool - Web search with retry, backoff, and rate limiting.

Implements exponential backoff retry logic, rate limiting for free tier (1000 req/month),
and structured metadata extraction from search results.
"""
import os
import time
import asyncio
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from tavily import AsyncTavilyClient, TavilyClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)


@dataclass
class RateLimiter:
    """Rate limiter for Tavily free tier (1000 requests/month)."""
    
    max_requests_month: int = 1000
    current_count: int = 0
    reset_date: datetime = field(default_factory=lambda: datetime.now().replace(day=1))
    request_timestamps: list[float] = field(default_factory=list)
    
    def can_request(self) -> bool:
        """Check if we can make another request."""
        now = datetime.now()
        if now.month != self.reset_date.month:
            self.current_count = 0
            self.reset_date = now.replace(day=1)
            self.request_timestamps = []
        
        if self.current_count >= self.max_requests_month:
            return False
        
        one_minute_ago = time.time() - 60
        self.request_timestamps = [
            ts for ts in self.request_timestamps if ts > one_minute_ago
        ]
        if len(self.request_timestamps) >= 10:
            return False
        
        return True
    
    def record_request(self) -> None:
        """Record a request timestamp."""
        self.current_count += 1
        self.request_timestamps.append(time.time())
    
    def get_remaining(self) -> int:
        """Get remaining requests for current month."""
        now = datetime.now()
        if now.month != self.reset_date.month:
            return self.max_requests_month
        return max(0, self.max_requests_month - self.current_count)


class TavilyTool:
    """Tavily search tool with retry logic, rate limiting, and metadata extraction."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        
        self.client = TavilyClient(api_key=self.api_key)
        self.async_client = AsyncTavilyClient(api_key=self.api_key)
        self.rate_limiter = RateLimiter()
        
        self.search_depth = os.getenv("TAVILY_SEARCH_DEPTH", "advanced")
        self.max_results = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
        self.days = int(os.getenv("TAVILY_DAYS", "3"))
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(__name__, "WARNING"),
    )
    def search(
        self,
        query: str,
        search_depth: Optional[str] = None,
        max_results: Optional[int] = None,
        days: Optional[int] = None,
        topic: str = "general",
        include_answer: bool = True,
        include_raw_content: bool = False,
    ) -> dict[str, Any]:
        """
        Perform synchronous web search with retry logic.
        
        Args:
            query: Search query string
            search_depth: 'basic' or 'advanced'
            max_results: Maximum results (1-100)
            days: Filter results from last N days
            topic: 'general', 'news', or 'finance'
            include_answer: Include AI-generated answer
            include_raw_content: Include full page content
            
        Returns:
            Dictionary with results, metadata, and optional answer
        """
        if not self.rate_limiter.can_request():
            raise Exception("Rate limit exceeded. Wait for monthly reset.")
        
        self.rate_limiter.record_request()
        
        params = {
            "query": query,
            "search_depth": search_depth or self.search_depth,
            "max_results": max_results or self.max_results,
            "topic": topic,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
        }
        
        if days:
            params["days"] = days
        
        raw_response = self.client.search(**params)
        
        return self._extract_metadata(raw_response)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        before_sleep=before_sleep_log(__name__, "WARNING"),
    )
    async def async_search(
        self,
        query: str,
        search_depth: Optional[str] = None,
        max_results: Optional[int] = None,
        days: Optional[int] = None,
        topic: str = "general",
        include_answer: bool = True,
    ) -> dict[str, Any]:
        """
        Perform asynchronous web search with retry logic.
        
        Args:
            query: Search query string
            search_depth: 'basic' or 'advanced'
            max_results: Maximum results (1-100)
            days: Filter results from last N days
            topic: 'general', 'news', or 'finance'
            include_answer: Include AI-generated answer
            
        Returns:
            Dictionary with results, metadata, and optional answer
        """
        if not self.rate_limiter.can_request():
            raise Exception("Rate limit exceeded. Wait for monthly reset.")
        
        self.rate_limiter.record_request()
        
        params = {
            "query": query,
            "search_depth": search_depth or self.search_depth,
            "max_results": max_results or self.max_results,
            "topic": topic,
            "include_answer": include_answer,
        }
        
        if days:
            params["days"] = days
        
        raw_response = await self.async_client.search(**params)
        
        return self._extract_metadata(raw_response)
    
    def _extract_metadata(self, raw_response: dict[str, Any]) -> dict[str, Any]:
        """
        Extract and structure metadata from Tavily response.
        
        Args:
            raw_response: Raw response from Tavily API
            
        Returns:
            Structured response with extracted metadata
        """
        results = []
        for item in raw_response.get("results", []):
            result = {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0.0),
                "published_date": item.get("published_date", ""),
                "raw_content": item.get("raw_content", ""),
                "domain": self._extract_domain(item.get("url", "")),
                "relevance_tier": self._get_relevance_tier(item.get("score", 0.0)),
            }
            results.append(result)
        
        return {
            "query": raw_response.get("query", ""),
            "answer": raw_response.get("answer", ""),
            "results": results,
            "total_results": raw_response.get("total_results", len(results)),
            "response_time": raw_response.get("response_time", 0.0),
            "search_depth": raw_response.get("search_depth", self.search_depth),
            "has_answer": bool(raw_response.get("answer")),
            "remaining_requests": self.rate_limiter.get_remaining(),
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc or ""
        except Exception:
            return ""
    
    def _get_relevance_tier(self, score: float) -> str:
        """Get relevance tier from score."""
        if score >= 0.9:
            return "high"
        elif score >= 0.7:
            return "medium"
        elif score >= 0.5:
            return "low"
        return "very_low"
    
    def get_rate_limit_info(self) -> dict[str, Any]:
        """Get current rate limit status."""
        return {
            "remaining": self.rate_limiter.get_remaining(),
            "max": self.rate_limiter.max_requests_month,
            "used": self.rate_limiter.current_count,
        }