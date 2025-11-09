# OpenGlia

Minimal framework for AI-driven systems research. Just prompts over fast-agent.

Based on the [Glia paper (arXiv:2510.27176)](https://arxiv.org/abs/2510.27176).

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

## Creating New Experiments

### Quick Start Template

```bash
# 1. Create experiment directory
mkdir -p experiments/my_experiment
cd experiments/my_experiment

# 2. Create problem definition
cat > problem.md << 'EOF'
Design an efficient algorithm for [your problem].

System overview:
[Describe your system, components, and how they interact]

Objective:
[What metric to optimize, e.g., minimize latency, maximize throughput]

Evaluation:
[How to run benchmarks, what outputs to check]
A baseline benchmark is at: [path/to/baseline]
Target: [performance goal, e.g., 30% improvement over baseline]

Constraints:
[Any limitations, e.g., don't modify X, must preserve Y]
EOF

# 3. Create setup script
cat > setup.sh << 'EOF'
#!/bin/bash
set -e

# Clone/setup your simulator or benchmark
# git clone https://github.com/your/simulator.git
# pip install -r requirements.txt
# Apply any patches or configurations

echo "Setup complete!"
EOF
chmod +x setup.sh

# 4. Create run script
cat > run.sh << 'EOF'
#!/bin/bash
set -e

# Create timestamped output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="generated/run_${TIMESTAMP}"
mkdir -p "${OUTPUT_DIR}"

# Run Glia agent
python -m openglia.workflows.glia \
    problem.md \
    "${OUTPUT_DIR}"

echo "Results saved to: ${OUTPUT_DIR}"
EOF
chmod +x run.sh

# 5. Run your experiment
./setup.sh
./run.sh
```

### Key Files Explained

**`problem.md`** - Agent's task description
- Describe the system architecture
- Define optimization objective
- Explain how to run benchmarks
- Specify baseline performance
- Set target goals

**`setup.sh`** - One-time environment setup
- Install dependencies
- Clone simulators/frameworks
- Apply configurations
- Register custom components

**`run.sh`** - Execute discovery
- Create timestamped output directory
- Call `openglia.workflows.glia`
- Save results and traces

### Example Project Structure

```
experiments/my_experiment/
├── problem.md              # What to optimize
├── setup.sh                # One-time setup
├── run.sh                  # Run discovery
├── fastagent.config.yaml   # Optional: agent configuration
├── environment/            # Your simulator/benchmark
│   ├── simulator/          # (gitignored, created by setup.sh)
│   ├── run_benchmark.sh    # Script agent can call
│   └── stubs/              # Starting point templates
└── generated/              # Outputs (gitignored)
    └── run_20250109_*/
        ├── solution.md
        ├── fastagent.jsonl
        └── final_code.py
```

### Tips for Success

1. **Make benchmarks fast** - Agent will run many iterations
2. **Clear metrics** - Output parseable performance numbers
3. **Good baseline** - Provide a simple working solution to improve upon
4. **Specific goals** - "30% better latency" is clearer than "improve performance"
5. **Observable state** - Log detailed metrics the agent can analyze

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

**Glia: A Human-Inspired AI for Automated Systems Design and Optimization**
[arXiv:2510.27176](https://arxiv.org/abs/2510.27176) | [PDF](arxiv_2510.27176.pdf)
