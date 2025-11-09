#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR/environment"
VIDUR_DIR="$ENV_DIR/vidur"

# Create timestamped output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="$SCRIPT_DIR/generated/run_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

# Create scratch directory for this run
SCRATCH_DIR="$OUTPUT_DIR/scratch"
mkdir -p "$SCRATCH_DIR"

echo "=== OpenGLIA Run $TIMESTAMP ==="
echo ""

# CRITICAL: Reset AI scheduler to clean stub before each run
echo "Resetting AI scheduler to stub..."
cp "$ENV_DIR/stubs/ai_global_scheduler_stub.py" \
   "$VIDUR_DIR/vidur/scheduler/global_scheduler/ai_global_scheduler.py"

# Clean previous results
if [ -d "$VIDUR_DIR/simulator_results" ]; then
    echo "Cleaning previous simulator results..."
    rm -rf "$VIDUR_DIR/simulator_results"
fi

# Export scratch directory for agent to use
export OPENGLIA_SCRATCH_DIR="$SCRATCH_DIR"
export OPENGLIA_RUN_ID="$TIMESTAMP"

# Run discovery from experiment directory
echo "Starting Glia discovery..."
cd "$SCRIPT_DIR"
python -m openglia.workflows.glia problem.md "$OUTPUT_DIR"

# Copy final scheduler for inspection
echo "Saving final scheduler..."
cp "$VIDUR_DIR/vidur/scheduler/global_scheduler/ai_global_scheduler.py" \
   "$OUTPUT_DIR/final_scheduler.py"

echo ""
echo "=== Run Complete ==="
echo "  Solution: $OUTPUT_DIR/solution.md"
echo "  Trace: $OUTPUT_DIR/fastagent.jsonl"
echo "  Final Scheduler: $OUTPUT_DIR/final_scheduler.py"
echo "  Scratch: $SCRATCH_DIR"
echo "  Vidur Results: $VIDUR_DIR/simulator_results/"
echo ""
