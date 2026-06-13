"""
Synthesizer Agent - Combines sources and refines briefs.
"""
from typing import Any, Optional

from scripts.tools.openrouter_tool import OpenRouterTool


class SynthesizerAgent:
    """Synthesizer that combines research into intelligence briefs."""
    
    def __init__(self):
        self.llm = OpenRouterTool()
    
    async def synthesize(
        self,
        query: str,
        dimensions: list[dict[str, Any]],
        tavily_results: list[dict[str, Any]],
        qdrant_context: list[dict[str, Any]],
    ) -> str:
        """
        Synthesize research into initial brief.
        
        Args:
            query: Original research query
            dimensions: Analysis dimensions
            tavily_results: Web search results
            qdrant_context: Historical context
            
        Returns:
            Synthesized intelligence brief
        """
        prompt = self._build_synthesis_prompt(
            query, dimensions, tavily_results, qdrant_context
        )
        
        system_prompt = """You are a senior intelligence analyst. 
Generate a comprehensive Intelligence Brief based on the provided research.
Structure the brief with clear sections and cite sources.
Separate facts from interpretation and projections."""
        
        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7,
        )
    
    async def refine(
        self,
        current_brief: str,
        critique: dict[str, Any],
        query: str,
    ) -> str:
        """
        Refine brief based on critique.
        
        Args:
            current_brief: Current version of the brief
            critique: Critique results
            query: Original query
            
        Returns:
            Refined intelligence brief
        """
        prompt = self._build_refinement_prompt(
            current_brief, critique, query
        )
        
        system_prompt = """You are a senior intelligence analyst.
Refine the Intelligence Brief based on the critique.
Address all weaknesses, fill gaps, and eliminate redundancies.
Maintain factual accuracy and clear source attribution."""
        
        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7,
        )
    
    def _build_synthesis_prompt(
        self,
        query: str,
        dimensions: list[dict[str, Any]],
        tavily_results: list[dict[str, Any]],
        qdrant_context: list[dict[str, Any]],
    ) -> str:
        """Build prompt for synthesis."""
        dim_names = ", ".join([d["name"].replace("_", " ") for d in dimensions])
        
        tavily_section = self._format_tavily_results(tavily_results)
        qdrant_section = self._format_qdrant_context(qdrant_context)
        
        return f"""Generate an Intelligence Brief for the following query:

QUERY: {query}

ANALYSIS DIMENSIONS: {dim_names}

RECENT NEWS AND INFORMATION (Tavily):
{tavily_section}

HISTORICAL CONTEXT (Qdrant):
{qdrant_section}

Please generate a comprehensive Intelligence Brief with:
1. Executive Summary (2-3 paragraphs)
2. Analysis by Dimension
3. Key Findings
4. Projections and Trends
5. Recommendations
6. Sources

Separate facts from interpretation. Cite all sources."""
    
    def _build_refinement_prompt(
        self,
        current_brief: str,
        critique: dict[str, Any],
        query: str,
    ) -> str:
        """Build prompt for refinement."""
        weaknesses = "\n".join([
            f"- {w}" for w in critique.get("weaknesses", [])
        ])
        gaps = "\n".join([
            f"- {g}" for g in critique.get("gaps", [])
        ])
        suggestions = "\n".join([
            f"- {s}" for s in critique.get("suggestions", [])
        ])
        
        return f"""Refine the following Intelligence Brief based on the critique:

ORIGINAL QUERY: {query}

CURRENT BRIEF:
{current_brief}

CRITIQUE - WEAKNESSES:
{weaknesses}

CRITIQUE - GAPS:
{gaps}

CRITIQUE - SUGGESTIONS:
{suggestions}

Please refine the brief by:
1. Addressing all identified weaknesses
2. Filling information gaps
3. Eliminating redundancies
4. Adding nuances and counter-arguments
5. Maintaining factual accuracy"""
    
    def _format_tavily_results(self, results: list[dict[str, Any]]) -> str:
        """Format Tavily results for prompt."""
        if not results:
            return "No recent results found."
        
        formatted = []
        for i, r in enumerate(results[:10], 1):
            title = r.get("title", "Untitled")
            content = r.get("content", "")[:300]
            url = r.get("url", "")
            score = r.get("score", 0)
            dimension = r.get("dimension", "general")
            
            formatted.append(
                f"{i}. [{dimension}] {title}\n"
                f"   Score: {score:.2f}\n"
                f"   URL: {url}\n"
                f"   Content: {content}...\n"
            )
        
        return "\n".join(formatted)
    
    def _format_qdrant_context(self, context: list[dict[str, Any]]) -> str:
        """Format Qdrant context for prompt."""
        if not context:
            return "No historical context found."
        
        formatted = []
        for i, c in enumerate(context[:5], 1):
            content = c.get("content", "")[:300]
            score = c.get("score", 0)
            category = c.get("category", "general")
            
            formatted.append(
                f"{i}. [{category}] (Score: {score:.2f})\n"
                f"   {content}...\n"
            )
        
        return "\n".join(formatted)