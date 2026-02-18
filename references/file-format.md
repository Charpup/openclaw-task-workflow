# Task Workflow V3 File Format

Complete specification for task-workflow markdown files.

## File Location

```
~/.openclaw/workspace/task_backlog/
└── task-workflow-progress-{YYYY-MM-DD}.md
```

## File Structure

```markdown
# Task Workflow Progress - {YYYY-MM-DD}

**Generated**: {ISO_TIMESTAMP}  
**Status**: 🟢 Active | 🟡 Archived  
**Auto-archive**: CST 00:00 next day

---

## 📋 Task List

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| {id} | {name} | {score} | {deps} | {status} | {batch} |

### 🔄 Migrated from Previous Day

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| {id} | {name} | {score} | {deps} | migrated | - |

---

## 📊 Progress Tracking

| Timestamp | Event | Details |
|-----------|-------|---------|
| {time} | {event} | {details} |

---

## 📈 Statistics

- **Total Tasks**: {n}
- **Completed**: {n}
- **Running**: {n}
- **Pending**: {n}
- **Completion Rate**: {pct}%

---

## ✅ Completion Checklist

- [ ] All tasks completed
- [ ] Progress reviewed
- [ ] File archived
```

## Field Definitions

### Task Fields

| Field | Type | Description |
|-------|------|-------------|
| ID | string | Unique task identifier |
| Task | string | Human-readable name |
| Complexity | float | 1.0-10.0 score |
| Dependencies | list | Task IDs that must complete first |
| Status | enum | pending, running, completed, failed, migrated |
| Batch | int | Scheduling batch number |

### Status Values

| Status | Emoji | Meaning |
|--------|-------|---------|
| pending | ⏳ | Waiting for dependencies |
| running | 🔄 | Currently executing |
| completed | ✅ | Done successfully |
| failed | ❌ | Error occurred |
| migrated | 📦 | Carried over from previous day |

## Migration Logic

On CST 0:00, the system:

1. Reads yesterday's file
2. Finds all `pending` and `running` tasks
3. Creates new file for today
4. Marks tasks as `migrated`
5. Resets status to `pending`
6. Keeps `completed` and `failed` for history

## Example File

```markdown
# Task Workflow Progress - 2026-02-19

**Generated**: 2026-02-19T00:00:00  
**Status**: 🟢 Active  
**Auto-archive**: CST 00:00 next day

---

## 📋 Task List

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| research-a | 调研方案A | 4.2 | - | ✅ Completed | 1 |
| research-b | 调研方案B | 3.0 | - | 🔄 Running | 1 |
| summary | 汇总分析 | 5.0 | research-a, research-b | ⏳ Pending | 2 |

### 🔄 Migrated from Previous Day

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| legacy-task | 遗留任务 | 3.5 | - | ⏳ Pending | - |

---

## 📊 Progress Tracking

| Timestamp | Event | Details |
|-----------|-------|---------|
| 08:00 | File Created | Daily workflow initialized |
| 08:15 | Tasks Scheduled | 4 tasks into 3 batches |
| 08:30 | Task Completed | 'research-a' completed |

---

## 📈 Statistics

- **Total Tasks**: 4 (1 migrated)
- **Completed**: 1
- **Running**: 1
- **Pending**: 2
- **Completion Rate**: 25%
```

## Programmatic Access

```python
from task_workflow import TaskWorkflowV3

workflow = TaskWorkflowV3("/path/to/backlog")

# Parse existing file
tasks = workflow.parse_markdown_file("2026-02-19")

# Create new file
workflow.create_markdown_file("2026-02-20", tasks)
```
