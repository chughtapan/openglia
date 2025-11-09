# OpenGlia

An open-source implementation of Glia - a human-inspired AI framework for automated systems design and optimization, based on the paper "Glia: A Human-Inspired AI for Automated Systems Design and Optimization" (arXiv:2510.27176).

## Overview

OpenGlia uses large language models (LLMs) in a multi-agent workflow to discover novel, interpretable algorithms for systems optimization. Unlike black-box ML approaches, OpenGlia employs white-box reasoning to understand WHY solutions work, producing human-readable designs with explanations.

## Key Features

- **Multi-Agent Architecture**: Researcher and Supervisor agents collaborate to explore solutions
- **White-Box Reasoning**: Hypothesis-driven exploration with interpretable results
- **Multiple Execution Strategies**: Single-context (SCG) and multi-context (MCG) modes
- **Proven Performance**: Reproduces paper's 42.5% improvement on LLM routing problem
- **Extensible Framework**: Adaptable to various systems optimization domains

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openglia.git
cd openglia

# Install dependencies
pip install -r requirements.txt

# Set up Claude API key
export ANTHROPIC_API_KEY="your-api-key"
```

## Quick Start

```python
from openglia import OpenGlia
from openglia.examples import LLMRoutingProblem

# Initialize OpenGlia with a problem
glia = OpenGlia(problem=LLMRoutingProblem())

# Run single-context exploration
solution = glia.run_scg()

# Or run parallel multi-context (recommended)
solution = glia.run_mcg_parallel(n=4)

print(f"Discovered algorithm: {solution.algorithm}")
print(f"Performance improvement: {solution.improvement}%")
print(f"Reasoning: {solution.explanation}")
```

## Architecture

OpenGlia consists of several key components:

### Core Agents
- **Researcher Agent**: Proposes hypotheses, designs experiments, analyzes results
- **Supervisor Agent**: Guides exploration, asks probing questions, prevents plateaus

### Execution Strategies
- **SCG (Single-Context Glia)**: One coherent exploration chain
- **MCG-Par4**: 4 parallel instances with best-of-N selection
- **MCG-Seq**: Sequential execution with early stopping

### Reasoning Pipeline
- Hypothesis formation with evidence
- Experiment design and execution
- Statistical analysis and insight extraction
- Algorithm synthesis from insights

## Example: LLM Inference Routing

OpenGlia can discover optimal request routing algorithms for distributed LLM serving:

```python
# The system discovers that naive routing causes memory exhaustion
# Leading to request restarts and performance degradation

# OpenGlia's discovered solution: Head-Room Allocator (HRA)
# - Reserves memory headroom at admission time
# - Combines with shortest-job-first scheduling
# - Reduces restart rate from 26% to <1%
# - Achieves 42.5% latency improvement
```

## Performance

Based on the original paper's results:

| Metric | Baseline (LLQ) | OpenGlia (HRA) | Improvement |
|--------|---------------|----------------|-------------|
| Mean Latency | 40s | 23s | 42.5% |
| Restart Rate | 26% | <1% | 96% reduction |
| Discovery Time | 2 weeks (human) | 2 hours | 168x faster |

## Project Structure

```
openglia/
├── core/           # Agent implementations
├── orchestration/  # Multi-agent coordination
├── reasoning/      # Hypothesis and analysis
├── evaluation/     # Simulator interfaces
├── prompts/        # System and user prompts
├── utils/          # Utilities and API clients
├── examples/       # Case studies
└── tests/          # Test suite
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Citation

If you use OpenGlia in your research, please cite:

```bibtex
@article{glia2024,
  title={Glia: A Human-Inspired AI for Automated Systems Design and Optimization},
  author={Hamadanian, Pouya and others},
  journal={arXiv preprint arXiv:2510.27176},
  year={2024}
}
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This implementation is based on the Glia paper by researchers at MIT CSAIL. The original paper demonstrated the effectiveness of human-inspired AI for systems optimization.

## Status

🚧 **Under Active Development** - Core framework being implemented

See [IMPLEMENTATION_PROGRESS.md](../IMPLEMENTATION_PROGRESS.md) for current status.