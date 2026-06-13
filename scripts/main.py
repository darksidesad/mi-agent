"""
Intelligence Brief Generator - Main entry point.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from scripts.graph.workflow import run_pipeline, create_workflow
from scripts.graph.state import AgentState, create_initial_state
from scripts.loops.iteration_manager import IterationManager


async def main():
    """Main entry point for the Intelligence Brief Generator."""
    print("=" * 60)
    print("INTELLIGENCE BRIEF GENERATOR")
    print("=" * 60)
    print()
    
    query = input("Enter your research query: ").strip()
    
    if not query:
        print("Error: Query cannot be empty")
        return
    
    print(f"\nQuery: {query}")
    print("-" * 60)
    
    print("\nStarting pipeline...")
    print("1. Decomposing query into dimensions...")
    print("2. Researching (Tavily + Qdrant)...")
    print("3. Synthesizing sources...")
    print("4. Self-critique and refinement...")
    print("5. Validating quality...")
    print()
    
    manager = IterationManager()
    result = await manager.run_pipeline(query)
    
    print("\n" + "=" * 60)
    print("INTELLIGENCE BRIEF")
    print("=" * 60)
    print()
    print(result.get("synthesized_brief", "No brief generated"))
    print()
    print("-" * 60)
    print(f"Quality Score: {result.get('quality_score', 0)}/10")
    print(f"Iterations: {result.get('loop_iteration', 0)}")
    print(f"Complete: {result.get('is_complete', False)}")
    print("=" * 60)


async def run_interactive():
    """Run interactive mode."""
    while True:
        print("\n1. Generate Brief")
        print("2. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            await main()
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


async def run_single(query: str):
    """Run single query mode."""
    manager = IterationManager()
    result = await manager.run_pipeline(query)
    
    print("\n" + "=" * 60)
    print("INTELLIGENCE BRIEF")
    print("=" * 60)
    print()
    print(result.get("synthesized_brief", "No brief generated"))
    print()
    print("-" * 60)
    print(f"Quality Score: {result.get('quality_score', 0)}/10")
    print(f"Iterations: {result.get('loop_iteration', 0)}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(run_single(query))
    else:
        asyncio.run(run_interactive())