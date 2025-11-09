"""OpenGlia - Shared agent creation and discovery runner."""

import asyncio
import shutil
from pathlib import Path

from fast_agent import FastAgent, RequestParams
from fast_agent.mcp.prompt_serialization import save_messages

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
RESEARCHER_PROMPT = (PROMPTS_DIR / "researcher.md").read_text()
SUPERVISOR_PROMPT = (PROMPTS_DIR / "supervisor.md").read_text()


async def create_openglia_agents() -> FastAgent:
    """Create researcher and supervisor agents with shell access."""
    fast = FastAgent("OpenGlia")
    await fast.app.initialize()
    setattr(fast.app.context, "shell_runtime", True)

    @fast.agent(
        name="researcher",
        instruction=RESEARCHER_PROMPT,
        request_params=RequestParams(maxTokens=64000, max_iterations=1000, use_history=True, temperature=1.0),
    )
    async def researcher() -> None:
        pass

    @fast.agent(
        name="supervisor",
        instruction=SUPERVISOR_PROMPT,
        request_params=RequestParams(maxTokens=64000, max_iterations=100, use_history=True, temperature=1.0),
    )
    async def supervisor() -> None:
        pass

    @fast.evaluator_optimizer(
        name="scg", generator="researcher", evaluator="supervisor", min_rating="EXCELLENT", max_refinements=20
    )
    async def scg() -> None:
        pass

    return fast


async def run_discovery(problem_file: Path, output_dir: Path) -> str:
    """Run discovery and save outputs to timestamped directory."""
    problem = problem_file.read_text()

    print("Starting discovery...")
    print(f"Output: {output_dir}")

    fast = await create_openglia_agents()
    async with fast.run() as agent:
        result = await agent.scg.send(problem)

    # Save outputs
    (output_dir / "solution.md").write_text(result)

    # Save agent transcripts
    save_messages(agent.researcher.llm.message_history, str(output_dir / "researcher_transcript.jsonl"))
    save_messages(agent.supervisor.llm.message_history, str(output_dir / "supervisor_transcript.jsonl"))

    # Copy default trace if exists
    trace = Path("fastagent.jsonl")
    if trace.exists():
        shutil.copy(trace, output_dir / "fastagent.jsonl")
        trace.unlink()

    print(f"\n{'=' * 80}")
    print(f"COMPLETE - {output_dir}")
    print(f"{'=' * 80}")

    return result


def main() -> None:
    """CLI entry point for running discovery."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m openglia.workflows.glia <problem_file> <output_dir>")
        sys.exit(1)

    problem_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    asyncio.run(run_discovery(problem_file, output_dir))


if __name__ == "__main__":
    main()
