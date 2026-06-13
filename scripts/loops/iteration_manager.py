"""
Iteration Manager - Loop Engineering: critique → refine → validate.
"""
import time
from typing import Any

from scripts.graph.state import AgentState, create_initial_state
from scripts.agents.orchestrator import OrchestratorAgent


class IterationManager:
    """Manages loop iterations: research ONCE, then critique→refine→validate loop."""

    def __init__(
        self,
        max_iterations: int = 5,
        timeout_seconds: int = 600,
        quality_threshold: float = 8.0,
    ):
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.quality_threshold = quality_threshold
        self.orchestrator = OrchestratorAgent()

    async def run_pipeline(self, query: str) -> AgentState:
        start_time = time.time()
        state = create_initial_state(query)

        print(f"[1/3] Decomposing query...")
        state = await self.orchestrator.decompose_query(state)
        print(f"  Dimensions: {len(state['analysis_dimensions'])}")

        print(f"[2/3] Researching (Tavily + Qdrant)...")
        state = await self.orchestrator.research_parallel(state)
        print(f"  Tavily: {len(state.get('tavily_results', []))} results")
        print(f"  Qdrant: {len(state.get('qdrant_context', []))} results")

        print(f"[3/3] Synthesizing initial brief...")
        state = await self.orchestrator.synthesize(state)
        print(f"  Brief length: {len(state.get('synthesized_brief', '') or '')} chars")

        for iteration in range(self.max_iterations):
            elapsed = time.time() - start_time
            if elapsed > self.timeout_seconds:
                print(f"  Timeout reached after {elapsed:.1f}s")
                break

            state["loop_iteration"] = iteration + 1
            print(f"\n  --- Loop {iteration + 1}/{self.max_iterations} ---")

            state = await self.orchestrator.self_critique(state)
            state = await self.orchestrator.refine(state)
            state = await self.orchestrator.validate(state)

            score = state.get("quality_score", 0.0)
            print(f"  Score: {score}/10")

            if score >= self.quality_threshold:
                state["is_complete"] = True
                print(f"  Quality threshold reached!")
                break

        state = await self.orchestrator.deliver(state)

        elapsed = time.time() - start_time
        print(f"\nPipeline completed in {elapsed:.1f}s with score {state['quality_score']}")

        return state

    def get_stats(self) -> dict[str, Any]:
        return {
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "quality_threshold": self.quality_threshold,
        }
