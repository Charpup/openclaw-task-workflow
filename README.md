# Task Workflow v3.2 — DAG-Based Task Scheduler

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
- **Cross-session Persistence**: Daily backlog files with CST 00:00 auto-migration
- **Cycle Detection**: Refuses to schedule circular dependencies

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
planning-with-files (plan) → task-workflow (schedule) → tdd-sdd-development (implement)
```

Coordinates via `triadev-handoff.json` — reads extracted tasks, writes batch schedule. Also works standalone: reads `task_plan.md` directly when no handoff.json is present.

## What's New in v3.2

| Addition | Purpose |
|----------|---------|
| `examples/humanizer-skill-schedule/` | **GOLD** real-run reference — 21-task humanizer-skill project with input task_plan, full DAG output, and handoff snippet. Shows fan-out (T7 → 5 tasks), fan-in (T13 ← 5 tasks), critical path (12 tasks, complexity sum 35), max parallelism (5). |
| `evals/evals.json` (4 → 8 cases) | New cases: within-batch complexity ordering, cross-session migration (CST 00:00 behavior), standalone mode (no triadev-handoff), dynamic insertion mid-execution. ~80% deterministic assertions (sequence_order, json_path_*, file_exists). |

## Project Structure

```
openclaw-task-workflow/
├── SKILL.md                                  # Scheduling workflow
├── README.md                                 # This file
├── cli.py                                    # Entry point
├── pytest.ini                                # Test config
├── contracts/
│   └── stack-handshake.json                  # TriaDev integration contract
├── references/
│   ├── file-format.md                        # Daily file format spec (v3)
│   └── v3-migration.md                       # Migration guide from earlier versions
├── scripts/
│   ├── task_scheduler.py                     # DAG sort + batch grouping
│   ├── task_persistence.py                   # File persistence + daily migration
│   ├── task_index_manager.py                 # Cross-session index
│   └── stack_contract.py                     # Contract validator
├── config/
│   └── cron.yaml                             # Auto-migration config (CST 00:00)
├── examples/
│   └── humanizer-skill-schedule/             # GOLD — real 21-task project
├── evals/
│   └── evals.json                            # 8 cases
└── tests/                                    # Unit + integration
```

## Working Example

See [`examples/humanizer-skill-schedule/`](examples/humanizer-skill-schedule/) for a real completed run — the humanizer-skill build (PR blader/humanizer#94 merged). Demonstrates:

- Mixed complexities (1 to 7) with real reasoning
- Fan-out: one high-complexity task (T7 merge 32 patterns) unlocks 5 downstream references
- Fan-in: the main `SKILL.md` draft (T13) requires all 5 reference files
- Critical path length 12, total complexity sum 35, max parallelism 5
- Both raw `output-schedule.json` format and the triadev-handoff slice

## Changelog

### v3.2.0 (2026-04-18)
Round-2 standardization. Additive; no breaking changes.

- **New**: `examples/humanizer-skill-schedule/` — GOLD completed-run reference harvested from real humanizer-skill project. 4 files: README + input task_plan.md + output-schedule.json + handoff snippet.
- **Hardened**: `evals/evals.json` — 4 → 8 cases. New: complexity ordering within batches, cross-session migration behavior, standalone mode (no handoff.json), dynamic insertion. Shifted ~80% of assertions to deterministic types (`sequence_order`, `json_path_equals`, `file_exists`).

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
