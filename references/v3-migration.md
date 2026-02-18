# V2 to V3 Migration Guide

Upgrading from Task Workflow V2 to V3.

## What's New in V3

| Feature | V2 | V3 | Benefit |
|---------|-----|-----|---------|
| **File Persistence** | ❌ Session only | ✅ Markdown files | Cross-session tracking |
| **Progress Tracking** | ❌ In-memory | ✅ File-based | Survives restarts |
| **Auto Archive** | ❌ Manual | ✅ CST 0:00 daily | Automatic cleanup |
| **Cron Integration** | ❌ None | ✅ OpenClaw API | Scheduled tasks |

## Breaking Changes

### 1. Data Storage

**V2:**
```python
tasks = {}  # In-memory dict
```

**V3:**
```python
# Stored in markdown files
~/.openclaw/workspace/task_backlog/
└── task-workflow-progress-2026-02-19.md
```

### 2. API Changes

**V2:**
```python
from task_workflow import TaskWorkflow

workflow = TaskWorkflow()
workflow.add_task("id", {"name": "Task"})
```

**V3:**
```python
from task_workflow import TaskWorkflowV3

workflow = TaskWorkflowV3("/path/to/backlog")
workflow.init_daily_file()  # New: Initialize file first
workflow.add_task({"id": "id", "name": "Task"})
```

### 3. Status Values

**V2:** pending, running, completed, failed

**V3:** pending, running, completed, failed, **migrated**

## Migration Steps

### Step 1: Backup V2 Data

```python
# Export existing tasks
import json
from task_workflow import TaskWorkflow

v2 = TaskWorkflow()
v2.export_tasks("v2-backup.json")
```

### Step 2: Install V3

```bash
git clone https://github.com/Charpup/openclaw-task-workflow.git \
  ~/.openclaw/skills/task-workflow
```

### Step 3: Import to V3

```python
from task_workflow import TaskWorkflowV3
import json

# Load V2 backup
with open("v2-backup.json") as f:
    v2_tasks = json.load(f)

# Initialize V3
v3 = TaskWorkflowV3("~/.openclaw/workspace/task_backlog")
v3.init_daily_file()

# Import tasks
for task_id, task_data in v2_tasks.items():
    v3.add_task({
        "id": task_id,
        "name": task_data["name"],
        "complexity": task_data.get("complexity", 5.0),
        "dependencies": task_data.get("dependencies", []),
        "status": task_data.get("status", "pending")
    })
```

### Step 4: Setup Cron (Optional)

```bash
python -m task_workflow_v3.cli setup-cron
```

## Configuration Changes

### V2 Config
```python
# config.py
MAX_BATCH_SIZE = 10
```

### V3 Config
```python
# config.yaml
max_batch_size: 10
backlog_path: ~/.openclaw/workspace/task_backlog
cron:
  enabled: true
  daily_init: "0 0 * * *"
```

## Rollback Plan

If V3 doesn't work for you:

1. Stop using V3
2. Restore from `v2-backup.json`
3. Reinstall V2 version

```bash
cd ~/.openclaw/skills/task-workflow
git checkout v2.x
```

## FAQ

**Q: Can I use V2 and V3 together?**
A: No, they conflict. Choose one.

**Q: Will I lose my V2 tasks?**
A: Only if you don't backup. Follow Step 1.

**Q: Is V2 still supported?**
A: V2 is maintenance mode. V3 recommended.

---

For help, open an issue at https://github.com/Charpup/openclaw-task-workflow/issues
