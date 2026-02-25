# Task Workflow

[![Version](https://img.shields.io/badge/version-3.1.1-blue.svg)](https://github.com/Charpup/openclaw-task-workflow/releases/tag/v3.1.1)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-4CAF50.svg)](https://openclaw.ai)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![evals](https://img.shields.io/badge/evals-3%20cases-blueviolet.svg)](evals/evals.json)

> DAG-based intelligent task scheduling for OpenClaw agents. Resolves task dependencies via topological sort, scores complexity, and persists progress to daily markdown files across sessions.

智能任务调度系统 — 支持 DAG 依赖分析、复杂度排序、文件持久化追踪和自动归档。

---

## AI Agent Quick Reference

```yaml
# Skill identity (SKILL.md frontmatter)
name: task-workflow        # Note: was "task-workflow-v3" before v3.1.1
version: "3.1.1"
triggers:
  - "manage tasks with dependencies"
  - "schedule tasks"
  - "DAG dependency"
  - "task backlog"
  - "init daily task file"
  - "dependency resolution"

# Runtime requirements
requires:
  bins: [python3]
  env: []

# Install
run: pip3 install pyyaml
```

**When to invoke:**
- Managing 5+ interdependent tasks that span multiple sessions
- Need automatic dependency resolution (topological sort / DAG)
- Want complexity-based task batching and ordering
- Need persistent cross-session progress tracking with auto-migration

**When NOT to invoke:**
- Simple sequential tasks with no dependencies
- Single-session, quick one-off work (< 3 tasks)

---

## Features

| Feature | Description |
|---------|-------------|
| **DAG Scheduling** | Topological sort for correct dependency ordering |
| **Complexity Scoring** | 1–10 scale; lower = scheduled earlier in a batch |
| **Dynamic Insertion** | Add tasks mid-execution without restart |
| **File Persistence** | Daily markdown in `~/.openclaw/workspace/task_backlog/` |
| **Auto Migration** | Midnight CST moves pending tasks to next day's file |
| **Cron Integration** | OpenClaw Cron API support for daily init and cleanup |

---

## Installation

```bash
git clone https://github.com/Charpup/openclaw-task-workflow.git \
  ~/.openclaw/skills/task-workflow
pip3 install pyyaml
```

---

## Quick Start

### Python API

```python
from lib.task_scheduler import TaskScheduler, TaskNode

tasks = [
    TaskNode(id="research",   name="Research API options", estimated_time="medium"),
    TaskNode(id="implement",  name="Implement solution",   estimated_time="long",  depends_on=["research"]),
    TaskNode(id="test",       name="Write tests",          estimated_time="short", depends_on=["implement"]),
    TaskNode(id="deploy",     name="Deploy to prod",       estimated_time="short", depends_on=["test"]),
]

scheduler = TaskScheduler(enable_persistence=True)
batches = scheduler.schedule_tasks(tasks)
# Batch 1: research
# Batch 2: implement
# Batch 3: test
# Batch 4: deploy
```

### CLI

```bash
# Initialize today's task file
python3 cli.py init-daily

# Add tasks
python3 cli.py add research "Research API options" --time medium
python3 cli.py add implement "Implement solution" --time long --depends-on research

# List tasks (shows dependency order and current status)
python3 cli.py list

# Update status
python3 cli.py update research completed --notes "Chose REST API with OAuth"

# Log work detail
python3 cli.py log implement --detail "Started, need to handle token refresh"

# Run demo
python3 cli.py demo
```

---

## File Persistence

Progress is saved to daily markdown files at:

```
~/.openclaw/workspace/task_backlog/
├── task-workflow-progress-2026-02-24.md   # archived
├── task-workflow-progress-2026-02-25.md   # today (active)
└── task-workflow-progress-2026-02-26.md   # pre-created
```

Each file contains:
- Task definitions with IDs, status, dependencies, and complexity scores
- Batch schedule (dependency-ordered groups)
- Session logs per task
- Timestamps for all state transitions

Pending tasks auto-migrate to the next day's file at midnight CST.

---

## Complexity Scoring Guide

| Score | Meaning | Examples |
|-------|---------|---------|
| 1–3 | Simple, well-understood | Documentation, config changes |
| 4–6 | Moderate, some unknowns | New API integration, refactor |
| 7–10 | Complex, high uncertainty | Distributed system design, perf optimization |

Lower complexity = scheduled earlier within a batch (to unblock dependents sooner).

---

## Cron Configuration

```bash
python3 cli.py setup-cron
```

Default schedule (uses OpenClaw Cron API):

| Schedule | Job |
|----------|-----|
| `0 0 * * *` (midnight CST) | Initialize new daily task file |
| `0 1 * * *` (1 AM CST) | Clean up files older than 30 days |

---

## Evals

Test cases in [`evals/evals.json`](evals/evals.json) follow the skill-creator standard:

| ID | Scenario | Expected Trigger |
|----|----------|-----------------|
| 1 | Schedule 5 tasks with DAG dependencies | ✅ Yes |
| 2 | Initialize today's daily task file | ✅ Yes |
| 3 | Mark a task completed with notes | ✅ Yes |

---

## Version History

| Version | Changes |
|---------|---------|
| **v3.1.1** | Fix `name: task-workflow-v3` → `name: task-workflow` (kebab-case compliance); add `metadata.openclaw`; add `evals/evals.json` |
| **v3.0.0** | V3 rewrite: file persistence, auto-archive, cron integration, `cli.py` |

---

## Integration: TriadDev Golden Triangle

This skill is the scheduling backbone of the **TriadDev** workflow:

```
📋 planning-with-files   →   📊 task-workflow   →   🧪 tdd-sdd-development
  (task_plan.md)              (batch schedule)         (SPEC.yaml + tests)
```

Use [triadev](https://github.com/Charpup/triadev) to orchestrate all three with one command.

---

## Testing

```bash
pytest tests/ -v
```

---

## License

MIT — [Charpup](https://github.com/Charpup)
