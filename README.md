# Task Workflow v3.1 — DAG-Based Task Scheduler

Intelligent task scheduling skill for AI coding agents. Uses dependency analysis,
complexity scoring, and topological sorting to produce optimal execution batches.

## What It Does

```
Tasks with dependencies → DAG analysis → Batch schedule (parallel where possible)
```

- **DAG Scheduling**: Topological sort for dependency resolution
- **Complexity Scoring**: 1-10 scale, lower complexity tasks execute first
- **Batch Grouping**: Independent tasks grouped for parallel execution
- **Dynamic Insertion**: Add tasks mid-execution without restart

## Installation

```bash
# Claude Code
claude skill add Charpup/openclaw-task-workflow

# Manual
git clone https://github.com/Charpup/openclaw-task-workflow.git ~/.claude/skills/task-workflow
```

## Part of the Golden Triangle

Task-workflow integrates with [TriaDev](https://github.com/Charpup/triadev):

```
planning-with-files (plan) → task-workflow (schedule) → tdd-sdd (implement)
```

Coordinates via `triadev-handoff.json` — reads extracted tasks, writes batch schedule.

## Project Structure

```
openclaw-task-workflow/
├── SKILL.md                  # Scheduling instructions
├── scripts/
│   ├── task_scheduler.py     # DAG sort + batch grouping
│   ├── task_persistence.py   # State persistence
│   └── task_index_manager.py # Cross-session index
├── references/
│   ├── file-format.md        # Daily file format spec
│   └── v3-migration.md       # Migration guide
├── contracts/
│   └── stack-handshake.json  # TriaDev integration contract
├── evals/
│   └── evals.json            # Test cases
└── tests/                    # Unit + integration tests
```

## Changelog

### v3.1.0 (2026-04-09)
- **New**: Prompt-centric SKILL.md with clear boundary rules
- **New**: Integration with triadev-handoff.json contract
- **Changed**: Moved lib/ to scripts/ (standalone executables)
- **Removed**: lib/subagent_monitor.py, lib/task_persistence_v31.py (legacy)
- **Removed**: config/cron-api-payload.json (OpenClaw-specific)

### v3.0.0
- File-based persistence, auto-archiving, cron integration

## License

MIT
