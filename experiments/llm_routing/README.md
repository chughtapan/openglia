# LLM Request Routing - OpenGLIA Experiment

Reproduce Glia paper's LLM routing discovery with proper environment management.

## Key Features

- **Pinned Simulator**: Vidur @ commit `8383d29` for reproducibility
- **Clean State**: Each run starts from stub template
- **AI Scheduler Registration**: Properly integrated into Vidur
- **Scratch Folders**: Isolated workspace per run

## Setup

```bash
./setup.sh  # One-time setup: clones Vidur, registers AI scheduler, installs stub
```

This will:
1. Clone Vidur simulator (pinned to specific commit)
2. Install dependencies
3. Register AI scheduler in Vidur's type system and registry
4. Install stub template as starting point

## Run Experiment

```bash
./run.sh    # Each run creates timestamped folder in generated/
```

Each run:
1. **Resets** AI scheduler to clean stub
2. Creates unique scratch directory
3. Runs Glia agent discovery
4. Saves final scheduler and results

## Structure

```
experiments/llm_routing/
├── setup.sh                          # One-time setup
├── run.sh                            # Run discovery (resets to stub each time)
├── problem.md                        # Problem definition for agent
├── environment/
│   ├── stubs/
│   │   └── ai_global_scheduler_stub.py   # Clean starting point (NEVER MODIFIED)
│   ├── vidur_overrides/
│   │   ├── global_scheduler_type.py      # Adds AI = 4 to enum
│   │   └── global_scheduler_registry.py  # Registers AIGlobalScheduler
│   ├── run_baseline.sh               # Baseline benchmark script
│   ├── run_all.sh                    # AI scheduler benchmark script
│   └── vidur/                        # Cloned simulator (gitignored)
│       └── vidur/scheduler/global_scheduler/
│           └── ai_global_scheduler.py    # Working copy (reset each run)
└── generated/                        # Timestamped outputs (gitignored)
    └── run_20250108_143022/
        ├── solution.md               # Final solution
        ├── fastagent.jsonl           # Agent trace
        ├── final_scheduler.py        # Discovered algorithm
        └── scratch/                  # Temporary files for this run
```

## How It Works

### Registration

Vidur needs to know about the AI scheduler:
- `vidur_overrides/global_scheduler_type.py` - Adds `AI = 4` to the enum
- `vidur_overrides/global_scheduler_registry.py` - Registers the class

These files are copied over Vidur's originals during setup.

### Clean State Per Run

The stub template (`environment/stubs/ai_global_scheduler_stub.py`) contains a simple random scheduler.

**CRITICAL**: Before each run, `run.sh` copies the stub to the working location:
```bash
cp environment/stubs/ai_global_scheduler_stub.py \
   environment/vidur/vidur/scheduler/global_scheduler/ai_global_scheduler.py
```

This ensures the agent always starts from the same baseline.

### Agent Workflow

1. Agent navigates via shell: `cd environment/vidur && ./run_all.sh`
2. Modifies `ai_global_scheduler.py` based on analysis
3. Runs benchmark, analyzes results
4. Iterates until target performance achieved

### Outputs

- **Vidur results**: `environment/vidur/simulator_results/` (cleaned each run)
- **Agent trace**: `generated/run_TIMESTAMP/fastagent.jsonl`
- **Final scheduler**: `generated/run_TIMESTAMP/final_scheduler.py`
- **Scratch space**: `generated/run_TIMESTAMP/scratch/` (for temp files)

## Environment Variables

Available to agent during run:
- `OPENGLIA_SCRATCH_DIR`: Path to scratch directory for this run
- `OPENGLIA_RUN_ID`: Timestamp identifier for this run

## Troubleshooting

**AI scheduler not found**:
```bash
# Re-run setup to reinstall overrides
./setup.sh
```

**Wrong Vidur version**:
```bash
# Setup auto-checks out pinned commit
rm -rf environment/vidur
./setup.sh
```

**Stale results**:
```bash
# run.sh auto-cleans simulator_results before each run
# Or manual clean:
rm -rf environment/vidur/simulator_results
```
