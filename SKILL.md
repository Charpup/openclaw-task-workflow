---
name: task-workflow
description: >-
  Intelligent task scheduling system with dependency analysis, complexity scoring, and file persistence. Use when managing multi-task projects with dependencies, need automatic batch scheduling, or require progress tracking across sessions. Supports DAG-based dependency resolution and automatic daily archiving.
---

# Task Workflow V3

智能任务调度系统 — 支持依赖分析、复杂度排序、动态任务插入、文件持久化追踪和自动归档。

## Quick Start

### 1. Initialize Workflow

```python
from task_workflow import TaskWorkflowV3

workflow = TaskWorkflowV3("/root/.openclaw/workspace/task_backlog")
workflow.init_daily_file()
```

### 2. Add Tasks

```python
tasks = [
    {
        "id": "research-a",
        "name": "调研方案A",
        "complexity": 4.2,
        "dependencies": [],
        "status": "pending"
    },
    {
        "id": "summary",
        "name": "汇总分析",
        "complexity": 5.0,
        "dependencies": ["research-a"],
        "status": "pending"
    }
]

for task in tasks:
    workflow.add_task(task)
```

### 3. Analyze and Schedule

```python
# Build dependency DAG and schedule batches
schedule = workflow.analyze_and_schedule()

# Output:
# Batch 1: research-a (complexity: 4.2)
# Batch 2: summary (complexity: 5.0, depends on: research-a)
```

### 4. Update Progress

```python
workflow.update_task_status("research-a", "completed")
workflow.update_task_status("summary", "running")
```

### 5. Check Status

```python
status = workflow.get_status()
print(f"Completed: {status['completed']}/{status['total']}")
```

## When to Use

**Use this skill when:**
- Managing projects with 5+ interdependent tasks
- Need automatic dependency resolution
- Want complexity-based task ordering
- Require persistent progress tracking
- Working across multiple sessions

**Skip when:**
- Simple sequential tasks without dependencies
- Quick one-off tasks
- Single-session work

## File Format

Workflow stores data in daily markdown files:

```
~/.openclaw/workspace/task_backlog/
├── task-workflow-progress-2026-02-18.md  # Yesterday (archived)
├── task-workflow-progress-2026-02-19.md  # Today (active)
└── task-workflow-progress-2026-02-20.md  # Tomorrow (pre-created)
```

See [references/file-format.md](references/file-format.md) for complete format specification.

## Key Features

| Feature | Description |
|---------|-------------|
| **DAG Scheduling** | Topological sort for dependency resolution |
| **Complexity Scoring** | 1-10 scale, lower = batch earlier |
| **Dynamic Insertion** | Add tasks mid-execution without restart |
| **Auto Migration** | CST 0:00 moves pending tasks to new day |
| **Cron Integration** | OpenClaw Cron API support |

## Dependencies

Task dependencies use simple ID references:

```python
{
    "id": "summary",
    "dependencies": ["research-a", "research-b"]
}
```

The system builds a DAG and schedules tasks in optimal batches.

## Complexity Scoring

Score tasks 1-10 based on:
- **1-3**: Simple, well-understood tasks
- **4-6**: Moderate complexity, some unknowns
- **7-10**: Complex, high uncertainty

Lower complexity tasks are batched first.

## Architecture

```
TaskWorkflowV3
├── init_daily_file()      # Create daily markdown
├── add_task()             # Add to queue
├── analyze_and_schedule() # Build DAG, create batches
├── update_task_status()   # Update progress
├── get_status()           # Report statistics
└── migrate_tasks()        # Daily auto-migration
```

## Cron Configuration

```yaml
# config/cron.yaml
cron_jobs:
  - name: task-workflow-daily-init
    schedule: "0 0 * * *"  # CST 0:00
    command: "python -m task_workflow_v3.cli init-daily"
  
  - name: task-workflow-cleanup
    schedule: "0 1 * * *"
    command: "python -m task_workflow_v3.cli cleanup --days 30"
```

## V2 to V3 Migration

| Feature | V2 | V3 |
|---------|-----|-----|
| File persistence | ❌ | ✅ Markdown files |
| Progress tracking | ❌ Session-only | ✅ File-based |
| Auto archive | ❌ | ✅ Daily migration |
| Cron integration | ❌ | ✅ OpenClaw API |

See [references/v3-migration.md](references/v3-migration.md) for full migration guide.

## References

- **File Format:** [references/file-format.md](references/file-format.md)
- **Migration Guide:** [references/v3-migration.md](references/v3-migration.md)
- **API Documentation:** See Python docstrings

---

*Task Workflow V3 — Intelligent scheduling for complex projects.*
