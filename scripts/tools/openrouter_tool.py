"""
OpenRouter Tool - Multi-model LLM client with fallback and streaming.

Supports multiple models via OpenRouter API with automatic fallback,
optional streaming, and token counting.
"""
import os
import asyncio
import time
from typing import Any, Optional, Generator, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

import httpx
from pydantic import BaseModel


class ModelTier(str, Enum):
    """Model tiers for different use cases."""
    FAST = "fast"
    STANDARD = "standard"
    REASONING = "reasoning"


@dataclass
class ModelConfig:
    """Model configuration."""
    name: str
    tier: ModelTier
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float


MODELS = {
    "nex-agi/nex-n2-pro:free": ModelConfig(
        name="nex-agi/nex-n2-pro:free",
        tier=ModelTier.STANDARD,
        max_tokens=8192,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
    "openai/gpt-4o-mini": ModelConfig(
        name="openai/gpt-4o-mini",
        tier=ModelTier.FAST,
        max_tokens=16384,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
    ),
    "anthropic/claude-sonnet-4-20250514": ModelConfig(
        name="anthropic/claude-sonnet-4-20250514",
        tier=ModelTier.REASONING,
        max_tokens=8192,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    "openai/gpt-4o": ModelConfig(
        name="openai/gpt-4o",
        tier=ModelTier.STANDARD,
        max_tokens=16384,
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
    ),
}


@dataclass
class TokenUsage:
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0


class OpenRouterTool:
    """OpenRouter multi-model LLM client with fallback."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        fast_model: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = default_model or os.getenv(
            "OPENROUTER_MODEL", "nex-agi/nex-n2-pro:free"
        )
        self.fast_model = fast_model or os.getenv(
            "OPENROUTER_FAST_MODEL", "nex-agi/nex-n2-pro:free"
        )
        
        self.total_usage = TokenUsage()
        self.max_cost_usd = float(os.getenv("MAX_COST_USD", "0.10"))
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        use_fast_model: bool = False,
    ) -> str:
        """
        Generate text using OpenRouter API.
        
        Args:
            prompt: User prompt
            model: Model to use (overrides default)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            use_fast_model: Use fast model instead of default
            
        Returns:
            Generated text
        """
        if self.total_usage.cost_usd >= self.max_cost_usd:
            raise Exception(f"Cost limit exceeded: ${self.max_cost_usd}")
        
        selected_model = model or (self.fast_model if use_fast_model else self.default_model)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        model_config = MODELS.get(selected_model)
        tokens = max_tokens or min(4096, model_config.max_tokens if model_config else 4096)
        
        try:
            result = await self._call_api(
                model=selected_model,
                messages=messages,
                max_tokens=tokens,
                temperature=temperature,
            )
            return result["content"] or ""
        except Exception as e:
            if selected_model != self.fast_model:
                print(f"Model {selected_model} failed, falling back to {self.fast_model}")
                return await self.generate(
                    prompt=prompt,
                    model=self.fast_model,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            raise
    
    async def generate_with_usage(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> tuple[str, TokenUsage]:
        """
        Generate text and return usage statistics.
        
        Returns:
            Tuple of (generated text, token usage)
        """
        if self.total_usage.cost_usd >= self.max_cost_usd:
            raise Exception(f"Cost limit exceeded: ${self.max_cost_usd}")
        
        selected_model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        model_config = MODELS.get(selected_model)
        tokens = max_tokens or min(4096, model_config.max_tokens)
        
        result = await self._call_api(
            model=selected_model,
            messages=messages,
            max_tokens=tokens,
            temperature=temperature,
        )
        
        usage = TokenUsage(
            prompt_tokens=result["usage"].get("prompt_tokens", 0),
            completion_tokens=result["usage"].get("completion_tokens", 0),
            total_tokens=result["usage"].get("total_tokens", 0),
            cost_usd=self._calculate_cost(
                selected_model,
                result["usage"].get("prompt_tokens", 0),
                result["usage"].get("completion_tokens", 0),
            ),
        )
        
        self.total_usage.prompt_tokens += usage.prompt_tokens
        self.total_usage.completion_tokens += usage.completion_tokens
        self.total_usage.total_tokens += usage.total_tokens
        self.total_usage.cost_usd += usage.cost_usd
        
        return result["content"], usage
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Generate text with streaming.
        
        Yields:
            Text chunks as they arrive
        """
        selected_model = model or self.default_model
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        model_config = MODELS.get(selected_model)
        tokens = max_tokens or min(4096, model_config.max_tokens)
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": selected_model,
                    "messages": messages,
                    "max_tokens": tokens,
                    "temperature": temperature,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
    
    async def get_embedding(
        self,
        text: str,
        model: str = "openai/text-embedding-3-small",
    ) -> list[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            model: Embedding model
            
        Returns:
            Embedding vector
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "input": text,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
    
    async def _call_api(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        """Make API call to OpenRouter with retry on rate limits."""
        import asyncio
        
        for attempt in range(6):
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 429:
                    wait = (2 ** attempt) * 10
                    print(f"  [LLM] Rate limited, waiting {wait}s (attempt {attempt + 1}/6)")
                    await asyncio.sleep(wait)
                    continue
                
                response.raise_for_status()
                data = response.json()
                return {
                    "content": data["choices"][0]["message"].get("content", ""),
                    "usage": data.get("usage", {}),
                }
        
        raise Exception("Rate limit: max retries exceeded")
    
    def _calculate_cost(
        self, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """Calculate cost in USD."""
        model_config = MODELS.get(model, MODELS[self.default_model])
        input_cost = (prompt_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (completion_tokens / 1000) * model_config.cost_per_1k_output
        return input_cost + output_cost
    
    def get_usage_stats(self) -> dict[str, Any]:
        """Get current usage statistics."""
        return {
            "prompt_tokens": self.total_usage.prompt_tokens,
            "completion_tokens": self.total_usage.completion_tokens,
            "total_tokens": self.total_usage.total_tokens,
            "cost_usd": round(self.total_usage.cost_usd, 6),
            "remaining_budget": round(self.max_cost_usd - self.total_usage.cost_usd, 6),
        }