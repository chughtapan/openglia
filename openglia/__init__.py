"""
OpenGlia - Human-inspired AI framework for systems optimization.

Based on the Glia paper (arXiv:2510.27176), OpenGlia implements a multi-agent
AI system for automated discovery of system algorithms and optimizations.

Key components:
- Researcher Agent: Forms hypotheses, designs experiments, analyzes results
- Supervisor Agent: Guides exploration, asks probing questions
- Evaluator-Optimizer: Iterative refinement loop (fast-agent pattern)
- Parallel Workflows: MCG-Par4 for scaling test-time compute

Framework: fast-agent with Anthropic Claude
"""

__version__ = "0.1.0"
