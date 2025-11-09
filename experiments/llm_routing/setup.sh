#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR/environment"
VIDUR_DIR="$ENV_DIR/vidur"
VIDUR_COMMIT="8383d29"  # Pin to specific commit for reproducibility

echo "=== OpenGLIA LLM Routing Experiment Setup ==="

# Clone Vidur if not exists
if [ ! -d "$VIDUR_DIR" ]; then
    echo "Cloning Vidur simulator..."
    git clone https://github.com/microsoft/vidur.git "$VIDUR_DIR"
    cd "$VIDUR_DIR"
    git checkout "$VIDUR_COMMIT"
else
    echo "Vidur already cloned"
    cd "$VIDUR_DIR"
    # Ensure we're on the right commit
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    if [ "$CURRENT_COMMIT" != "$VIDUR_COMMIT" ]; then
        echo "Checking out pinned commit $VIDUR_COMMIT..."
        git checkout "$VIDUR_COMMIT"
    fi
fi

# Install dependencies
echo "Installing Vidur dependencies..."
uv pip install -q -r requirements.txt

# Install registration overrides
echo "Installing AI scheduler registration..."
cp "$ENV_DIR/vidur_overrides/global_scheduler_type.py" \
   "$VIDUR_DIR/vidur/types/global_scheduler_type.py"

cp "$ENV_DIR/vidur_overrides/global_scheduler_registry.py" \
   "$VIDUR_DIR/vidur/scheduler/global_scheduler/global_scheduler_registry.py"

# Copy stub as initial scheduler
echo "Installing AI scheduler stub..."
cp "$ENV_DIR/stubs/ai_global_scheduler_stub.py" \
   "$VIDUR_DIR/vidur/scheduler/global_scheduler/ai_global_scheduler.py"

# Copy run scripts
echo "Installing experiment scripts..."
cp "$ENV_DIR/run_baseline.sh" "$VIDUR_DIR/"
cp "$ENV_DIR/run_all.sh" "$VIDUR_DIR/"
chmod +x "$VIDUR_DIR/run_baseline.sh" "$VIDUR_DIR/run_all.sh"

echo ""
echo "✓ Setup complete!"
echo ""
echo "Vidur commit: $VIDUR_COMMIT"
echo "Structure:"
echo "  - Simulator: $VIDUR_DIR"
echo "  - AI Scheduler: $VIDUR_DIR/vidur/scheduler/global_scheduler/ai_global_scheduler.py"
echo "  - Stub template: $ENV_DIR/stubs/ai_global_scheduler_stub.py"
echo ""
