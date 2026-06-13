"""
Orchestrator Agent - Main pipeline controller.
"""
import asyncio
import time
from typing import Any

from scripts.graph.state import AgentState
from scripts.agents.researcher import ResearcherAgent
from scripts.agents.synthesizer import SynthesizerAgent
from scripts.loops.self_critique import SelfCritiqueLoop


class OrchestratorAgent:
    """Main orchestrator for the intelligence brief pipeline."""
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.synthesizer = SynthesizerAgent()
        self.critique_loop = SelfCritiqueLoop()
    
    async def decompose_query(self, state: AgentState) -> AgentState:
        """
        Decompose user query into analysis dimensions.
        
        Product Owner Agent responsibility.
        """
        query = state["query"]
        
        dimensions = await self._identify_dimensions(query)
        
        return {
            **state,
            "analysis_dimensions": dimensions,
            "metadata": {
                **state.get("metadata", {}),
                "start_time": time.time(),
            },
        }
    
    async def research_parallel(self, state: AgentState) -> AgentState:
        """
        Execute parallel research using Tavily and Qdrant.
        
        Runs both searches simultaneously for efficiency.
        """
        query = state["query"]
        dimensions = state["analysis_dimensions"]
        
        tavily_task = self.researcher.search_tavily(query, dimensions)
        qdrant_task = self.researcher.search_qdrant(query, dimensions)
        
        tavily_results, qdrant_context = await asyncio.gather(
            tavily_task, qdrant_task, return_exceptions=True
        )
        
        if isinstance(tavily_results, Exception):
            print(f"Tavily search error: {tavily_results}")
            tavily_results = []
        
        if isinstance(qdrant_context, Exception):
            print(f"Qdrant search error: {qdrant_context}")
            qdrant_context = []
        
        return {
            **state,
            "tavily_results": tavily_results,
            "qdrant_context": qdrant_context,
        }
    
    async def synthesize(self, state: AgentState) -> AgentState:
        """
        Synthesize research into initial brief.
        
        Combines Tavily and Qdrant sources.
        """
        print(f"  [SYNTH] Tavily results: {len(state.get('tavily_results', []))}")
        print(f"  [SYNTH] Qdrant context: {len(state.get('qdrant_context', []))}")
        print(f"  [SYNTH] Dimensions: {len(state.get('analysis_dimensions', []))}")
        
        brief = await self.synthesizer.synthesize(
            query=state["query"],
            dimensions=state["analysis_dimensions"],
            tavily_results=state["tavily_results"],
            qdrant_context=state["qdrant_context"],
        )
        
        print(f"  [SYNTH] Brief length: {len(brief) if brief else 0}")
        
        return {
            **state,
            "synthesized_brief": brief,
            "loop_iteration": state.get("loop_iteration", 0) + 1,
        }
    
    async def self_critique(self, state: AgentState) -> AgentState:
        """
        Perform self-critique on the current brief.
        
        Loop Engineering core - identifies weaknesses and gaps.
        """
        critique = await self.critique_loop.critique_report(
            report=state["synthesized_brief"],
            query=state["query"],
        )
        
        return {
            **state,
            "critique": critique,
        }
    
    async def refine(self, state: AgentState) -> AgentState:
        """
        Refine brief based on critique.
        
        Loop Engineering - addresses identified issues.
        """
        if not state.get("critique"):
            return state
        
        if not state.get("synthesized_brief"):
            print("  [REFINE] No brief to refine, skipping")
            return state
        
        print(f"  [REFINE] Refining brief ({len(state['synthesized_brief'])} chars)")
        
        refined_brief = await self.synthesizer.refine(
            current_brief=state["synthesized_brief"],
            critique=state["critique"],
            query=state["query"],
        )
        
        print(f"  [REFINE] Refined length: {len(refined_brief) if refined_brief else 0}")
        
        if refined_brief:
            return {
                **state,
                "synthesized_brief": refined_brief,
            }
        
        return state
    
    async def validate(self, state: AgentState) -> AgentState:
        """
        Validate brief quality.
        
        QA Agent responsibility.
        """
        score = await self._validate_brief(
            brief=state["synthesized_brief"],
            dimensions=state["analysis_dimensions"],
        )
        
        return {
            **state,
            "quality_score": score,
        }
    
    async def deliver(self, state: AgentState) -> AgentState:
        """
        Deliver final brief.
        
        Stores results in Qdrant for future context.
        """
        end_time = time.time()
        start_time = state.get("metadata", {}).get("start_time", end_time)
        
        # Store results in Qdrant for future queries
        await self._store_results(state)
        
        return {
            **state,
            "is_complete": True,
            "metadata": {
                **state.get("metadata", {}),
                "end_time": end_time,
                "duration_seconds": end_time - start_time,
            },
        }
    
    async def _store_results(self, state: AgentState) -> None:
        """Store research results in Qdrant for future context."""
        brief = state.get("synthesized_brief", "")
        if not brief:
            return
        
        try:
            from scripts.tools.qdrant_tool import QdrantTool
            from scripts.tools.openrouter_tool import OpenRouterTool
            
            qdrant = QdrantTool()
            llm = OpenRouterTool()
            
            # Collect all sources from Tavily results
            sources = state.get("tavily_results", [])
            
            await qdrant.store_research(
                query=state["query"],
                brief=brief,
                sources=sources,
                dimensions=state.get("analysis_dimensions", []),
                embedding_func=llm.get_embedding,
            )
        except Exception as e:
            print(f"  [STORE] Warning: Could not store results: {e}")
    
    def should_continue(self, state: AgentState) -> str:
        """
        Decide whether to continue loop or deliver.
        
        Returns 'continue' to loop or 'complete' to deliver.
        """
        score = state.get("quality_score", 0.0)
        iteration = state.get("loop_iteration", 0)
        
        if score >= 8.0:
            return "complete"
        
        if iteration >= 5:
            return "complete"
        
        return "continue"
    
    async def _identify_dimensions(self, query: str) -> list[dict[str, Any]]:
        """Identify analysis dimensions from query."""
        dimensions = [
            {
                "name": "market_trends",
                "description": "Current market trends and dynamics",
                "priority": "high",
                "sources_required": 3,
            },
            {
                "name": "competitive_landscape",
                "description": "Key players and competitive positioning",
                "priority": "high",
                "sources_required": 3,
            },
            {
                "name": "regulatory_environment",
                "description": "Regulatory framework and compliance",
                "priority": "medium",
                "sources_required": 2,
            },
            {
                "name": "technology_innovation",
                "description": "Technological developments and innovation",
                "priority": "medium",
                "sources_required": 2,
            },
            {
                "name": "risk_factors",
                "description": "Potential risks and challenges",
                "priority": "medium",
                "sources_required": 2,
            },
        ]
        
        return dimensions
    
    async def _validate_brief(
        self, brief: str, dimensions: list[dict[str, Any]]
    ) -> float:
        """Validate brief quality and return score."""
        if not brief:
            return 0.0
        
        score = 0.0
        
        if len(brief) > 500:
            score += 2.0
        
        if len(brief) > 1000:
            score += 2.0
        
        if len(brief) > 2000:
            score += 2.0
        
        if "Executive Summary" in brief:
            score += 1.0
        
        if "Sources" in brief or "References" in brief:
            score += 1.0
        
        if "Recommendations" in brief:
            score += 1.0
        
        if any(dim["name"].replace("_", " ") in brief.lower() 
               for dim in dimensions):
            score += 1.0
        
        return min(score, 10.0)