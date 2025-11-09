# OpenGlia

> **Open source re-implementation of the Glia framework. Not affiliated with the original authors.**
>
> **⚠️ Work in Progress**

A minimal framework for AI-driven systems research and optimization. Enables autonomous agents to design, benchmark, and optimize complex systems through iterative experimentation.

📄 **Based on:** [Glia: A Human-Inspired AI for Automated Systems Design and Optimization](https://arxiv.org/abs/2510.27176) (arXiv:2510.27176)

## Quick Start

```bash
# Install
pip install -e .

# Set up API key
echo "ANTHROPIC_API_KEY=sk-..." > .env

# Run the LLM routing experiment
cd experiments/llm_routing
./setup.sh  # One-time environment setup
./run.sh    # Run discovery

# View results
cat generated/run_*/solution.md
```

## How It Works

1. Define your optimization problem in `problem.md`
2. Provide a benchmark environment the agent can execute
3. Run `openglia.workflows.glia` with your problem
4. Agent iteratively designs, tests, and refines solutions
5. Review the discovered solution and execution traces

```
experiments/your_experiment/
├── problem.md              # Problem definition
├── setup.sh                # Environment setup
├── run.sh                  # Run discovery
├── environment/            # Simulator/benchmark
└── generated/              # Agent outputs
    └── run_TIMESTAMP/
        ├── solution.md     # Final solution
        └── fastagent.jsonl # Execution trace
```

## Creating Custom Experiments

### 1. Define the Problem

Create `problem.md`:

```markdown
# Optimize [System Name]

## System Overview
[Describe architecture and components]

## Objective
Minimize [metric] while maintaining [constraint]

## Evaluation
Run benchmarks with: `./environment/run_benchmark.sh`
Baseline performance: [X ms/req]
Target: [Y ms/req] (30% improvement)

## Constraints
- Don't modify [protected components]
- Must preserve [behaviors]
```

### 2. Set Up Environment

Create `setup.sh`:

```bash
#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Clone or setup simulator
git clone https://github.com/your/simulator.git environment/simulator

echo "Setup complete!"
```

### 3. Create Run Script

Create `run.sh`:

```bash
#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="generated/run_${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

python -m openglia.workflows.glia problem.md "${OUTPUT_DIR}"

echo "Results: ${OUTPUT_DIR}/solution.md"
```

### 4. Execute

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

## Project Structure

```
openglia/
├── workflows/
│   └── glia.py           # Core agent orchestration (~100 lines)
├── prompts/
│   ├── researcher.md     # Research agent prompt
│   └── supervisor.md     # Supervisor agent prompt
└── utils/

experiments/
└── llm_routing/          # Example: LLM routing optimization
    ├── problem.md        # Problem definition
    ├── setup.sh          # Setup Vidur simulator
    ├── run.sh            # Execute discovery
    ├── environment/      # Vidur simulator (gitignored)
    └── generated/        # Results (gitignored)
```

## Tips for Success

- **Fast benchmarks**: Agents run many iterations; optimize for speed
- **Clear metrics**: Output parseable numbers (e.g., "latency: 45ms")
- **Good baseline**: Provide a working solution to improve upon
- **Specific goals**: "30% better latency" > "improve performance"
- **Observable state**: Log detailed metrics for agent analysis

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run checks
pre-commit run --all-files
```

## Reference

**Glia: A Human-Inspired AI for Automated Systems Design and Optimization**
arXiv:2510.27176 | [Paper](https://arxiv.org/abs/2510.27176) | [PDF](arxiv_2510.27176.pdf)

## License

MIT

---

*This is an independent open source implementation and is not affiliated with, endorsed by, or connected to the original Glia paper authors.*
