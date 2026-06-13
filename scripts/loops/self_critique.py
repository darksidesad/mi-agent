"""
Self-Critique Loop - Loop Engineering core implementation.
"""
import json
from typing import Any

from scripts.tools.openrouter_tool import OpenRouterTool


class SelfCritiqueLoop:
    """Loop Engineering - Self-critique and iteration."""
    
    def __init__(self):
        self.llm = OpenRouterTool()
    
    async def critique_report(
        self,
        report: str,
        query: str,
    ) -> dict[str, Any]:
        """
        Perform self-critique on the report.
        
        Args:
            report: Current report version
            query: Original research query
            
        Returns:
            Critique results with score and recommendations
        """
        prompt = self._build_critique_prompt(report, query)
        
        system_prompt = """You are a critical senior editor reviewing an Intelligence Brief.
Analyze the report critically and provide honest feedback.
Score the report on a scale of 0-10 based on:
- Completeness (are all dimensions covered?)
- Accuracy (are claims supported by evidence?)
- Balance (is there bias?)
- Clarity (is it well-structured?)
- Actionability (are recommendations specific?)

Return your analysis as JSON with the following structure:
{
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"],
    "gaps": ["information gaps"],
    "biases": ["detected biases"],
    "redundancies": ["redundant content"],
    "suggestions": ["improvement suggestions"],
    "score": 0-10,
    "should_continue": true/false
}"""
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            temperature=0.3,
        )
        
        if not response:
            return self._default_critique()
        
        try:
            critique = json.loads(response)
        except json.JSONDecodeError:
            critique = self._parse_critique_fallback(response)
        
        critique["should_continue"] = (
            critique.get("score", 0) < 8.0 and 
            len(critique.get("weaknesses", [])) > 0
        )
        
        return critique
    
    def _default_critique(self) -> dict[str, Any]:
        """Return default critique when LLM fails."""
        return {
            "strengths": [],
            "weaknesses": ["LLM did not return critique"],
            "gaps": [],
            "biases": [],
            "redundancies": [],
            "suggestions": ["Retry the pipeline"],
            "score": 5.0,
            "should_continue": True,
        }
    
    async def identify_gaps(
        self,
        report: str,
        query: str,
    ) -> list[dict[str, str]]:
        """
        Identify specific information gaps.
        
        Args:
            report: Current report
            query: Original query
            
        Returns:
            List of gaps with search queries
        """
        prompt = f"""Analyze this Intelligence Brief and identify specific information gaps:

REPORT:
{report}

ORIGINAL QUERY: {query}

For each gap, provide:
1. What information is missing
2. Why it's important
3. A specific search query to find this information

Return as JSON array:
[
    {
        "gap": "description of missing info",
        "importance": "why it matters",
        "search_query": "specific search query"
    }
]"""
        
        system_prompt = """You are an intelligence analyst identifying research gaps.
Be specific about what information is missing and why it matters.
Provide actionable search queries to fill each gap."""
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            temperature=0.3,
        )
        
        try:
            gaps = json.loads(response)
        except json.JSONDecodeError:
            gaps = []
        
        return gaps
    
    async def iterate_report(
        self,
        current_report: str,
        gaps: list[dict[str, str]],
        query: str,
    ) -> str:
        """
        Iterate on report based on gaps.
        
        Args:
            current_report: Current version
            gaps: Identified gaps
            query: Original query
            
        Returns:
            Improved report
        """
        if not gaps:
            return current_report
        
        gap_descriptions = "\n".join([
            f"- {g['gap']} (Importance: {g['importance']})"
            for g in gaps
        ])
        
        prompt = f"""Improve this Intelligence Brief by addressing the identified gaps:

CURRENT REPORT:
{current_report}

IDENTIFIED GAPS:
{gap_descriptions}

ORIGINAL QUERY: {query}

Please improve the report by:
1. Addressing each identified gap
2. Adding missing information
3. Strengthening weak sections
4. Maintaining overall coherence"""
        
        system_prompt = """You are a senior intelligence analyst improving a report.
Address all identified gaps while maintaining factual accuracy.
Ensure the improvements enhance the report's value and completeness."""
        
        return await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7,
        )
    
    def _build_critique_prompt(self, report: str, query: str) -> str:
        """Build critique prompt."""
        return f"""Critically analyze this Intelligence Brief:

ORIGINAL QUERY: {query}

REPORT:
{report}

Provide a thorough critique covering:
1. Strengths - What's done well?
2. Weaknesses - What needs improvement?
3. Gaps - What information is missing?
4. Biases - Is there any detected bias?
5. Redundancies - Is there repeated content?
6. Suggestions - Specific improvements?
7. Score - Rate 0-10 overall quality
8. Should Continue - Does it need more iterations?

Return as JSON."""
    
    def _parse_critique_fallback(self, response: str) -> dict[str, Any]:
        """Parse critique from unstructured response."""
        return {
            "strengths": [],
            "weaknesses": ["Unable to parse structured critique"],
            "gaps": [],
            "biases": [],
            "redundancies": [],
            "suggestions": ["Review report manually"],
            "score": 5.0,
            "should_continue": True,
        }