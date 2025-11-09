# OpenGlia

Minimal framework for AI-driven systems research. Just prompts over fast-agent.

Based on the Glia paper (arXiv:2510.27176) - see `arxiv_2510.27176.pdf`.

## Installation

```bash
pip install -e .
```

## Quick Start - LLM Routing

```bash
# Setup experiment
cd experiments/llm_routing
./setup.sh

# Run discovery
./run.sh

# View results
ls generated/run_*/
cat generated/run_20250108_143022/solution.md
```

## Structure

- `openglia/workflows/glia.py` - Shared agent code (~100 lines)
- `openglia/prompts/` - Shared prompts (researcher, supervisor)
- `experiments/llm_routing/` - LLM routing experiment
  - `setup.sh` - Setup environment
  - `run.sh` - Run discovery (creates timestamped output)
  - `environment/` - Vidur simulator (gitignored)
  - `generated/` - Timestamped runs

## How It Works

1. `run.sh` executes from `experiments/llm_routing/`
2. Calls shared `openglia.workflows.glia` with problem.md
3. Agent uses shell: `cd environment/vidur && ./run_all.sh`
4. Vidur outputs: `environment/vidur/simulator_results/` (gitignored)
5. Agent traces: `generated/run_TIMESTAMP/` (saved by glia.py)

## Adding New Experiments

1. Create `experiments/my_experiment/`
2. Add `problem.md`, `setup.sh`, `run.sh`
3. Use shared `python -m openglia.workflows.glia problem.md output_dir`
4. Outputs saved to timestamped directories

## Environment

Create `.env`:
```
ANTHROPIC_API_KEY=sk-...
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Setup pre-commit
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Paper Reference

See `arxiv_2510.27176.pdf` for the Glia paper.
