---
name: task-workflow
description: >-
  TRIGGER: task scheduling, dependency analysis, DAG scheduling, batch ordering,
  task dependencies, complexity scoring, multi-task project.
  Intelligent task scheduling with DAG-based dependency resolution, complexity scoring,
  and batch ordering. Reads tasks from task_plan.md (planning-with-files output),
  builds a dependency graph, and produces an optimal execution schedule.
  Use when managing 5+ interdependent tasks. NOT for simple sequential task lists.
---

# Task Workflow v3.1 — DAG-Based Task Scheduler

Schedule interdependent tasks into optimal execution batches using dependency analysis
and complexity scoring.

## Role in the Golden Triangle

Task-workflow sits between **planning** and **execution**:

```
task_plan.md (planning-with-files)
      ↓ extract tasks
task-workflow: build DAG → score complexity → batch tasks
      ↓ write schedule
triadev-handoff.json → execution (direct or via tdd-sdd)
```

**Boundary clarity:**
- task_plan.md is the **plan** (human-readable, managed by planning-with-files)
- triadev-handoff.json is the **schedule** (machine-readable, managed by task-workflow)
- progress.md is the **log** (managed by planning-with-files, not task-workflow)

## When to Use

**Use when:**
- Managing 5+ interdependent tasks
- Tasks have dependency relationships (B cannot start before A)
- Need to identify which tasks can run in parallel
- Working across multiple sessions and need persistent schedule state

**Skip when:**
- Simple sequential tasks (just do them in order)
- Fewer than 5 tasks with no dependencies
- Single-session quick work

## Core Workflow

### Step 1: Extract Tasks from task_plan.md

Read the existing `task_plan.md` and identify actionable work units.
Each task needs:

```json
{
  "id": "research-gateways",
  "name": "Research API gateway solutions",
  "complexity": 4,
  "dependencies": []
}
```

**Complexity scoring (1-10):**
- **1-3 (Simple):** Well-understood, single-file, < 5 tool calls
- **4-6 (Moderate):** Some exploration, multi-file, 5-15 tool calls
- **7-10 (Complex):** Significant unknowns, architecture decisions, > 15 tool calls

### Step 2: Build Dependency Graph (DAG)

Construct a directed acyclic graph from task dependencies:

```
research-gateways ──→ compare-options ──→ write-recommendation
                                    ↗
research-pricing  ──────────────────
```

**Validation rules:**
- All dependency IDs must reference existing tasks
- No circular dependencies allowed (detect and report cycles)
- Missing dependency = error, not silent skip

### Step 3: Topological Sort + Batch Grouping

1. Find all tasks with no unresolved dependencies (in-degree = 0)
2. Group them into a batch, sorted by complexity (lowest first)
3. Remove completed batch from graph, recalculate in-degrees
4. Repeat until all tasks are scheduled

**Output format (batches):**
```
Batch 1: [research-gateways, research-pricing]  (parallel, no deps)
Batch 2: [compare-options]                       (depends on batch 1)
Batch 3: [write-recommendation]                  (depends on batch 2)
```

### Step 4: Write Schedule to Handoff File

If used with triadev, write the schedule to `triadev-handoff.json`:

```json
{
  "scheduling": {
    "status": "complete",
    "batches": [
      ["research-gateways", "research-pricing"],
      ["compare-options"],
      ["write-recommendation"]
    ]
  }
}
```

### Step 5: Track Execution Progress

As tasks complete:
1. Update task status in the schedule
2. Check if next batch is unblocked (all dependencies satisfied)
3. **Before** marking a batch complete, invoke [`verification-before-completion`](../verification-before-completion/SKILL.md) skill to verify all task IDs in the batch appear in `triadev-handoff.json.implementation.completed` with matching counts
4. Report progress summary

## Dynamic Task Insertion

New tasks can be added mid-execution:

1. Define the new task with its dependencies
2. Re-run DAG analysis on remaining (non-completed) tasks
3. Insert into appropriate batch
4. Announce the schedule change

## Standalone Usage (Without TriaDev)

Task-workflow works independently. Without triadev-handoff.json:
- Read tasks from user input or task_plan.md directly
- Output schedule as formatted text
- Track progress in memory within the session

## Helper Scripts

Optional Python scripts in `scripts/` for deterministic computation:

| Script | Purpose | Usage |
|--------|---------|-------|
| `task_scheduler.py` | DAG sort + batch grouping | `python scripts/task_scheduler.py` |
| `task_persistence.py` | Daily file creation + task state persistence | `python scripts/task_persistence.py` |
| `task_index_manager.py` | Cross-session task index management | `python scripts/task_index_manager.py` |

These scripts are **optional** — Claude can perform DAG scheduling directly for small task sets (< 20 tasks). Use scripts for large task sets or when persistence across sessions is needed.

## Daily State Files (Optional)

For long-running projects, task-workflow can create daily state snapshots:

```
~/.openclaw/workspace/task_backlog/
├── task-workflow-progress-2026-04-08.md  (archived)
└── task-workflow-progress-2026-04-09.md  (active)
```

These are **machine state files** — structured task tables and progress events.
They are NOT human-facing session logs (that's progress.md's job).

Auto-migration at CST 00:00 moves pending tasks to the new day's file.

## Integration with TriaDev

When used as part of the Golden Triangle:

**What task-workflow reads:**
- `triadev-handoff.json` → `planning.tasks_extracted` (input tasks)

**What task-workflow writes:**
- `triadev-handoff.json` → `scheduling.batches` (output schedule)
- `triadev-handoff.json` → `scheduling.status` (pending → complete)

**What task-workflow does NOT do:**
- Does not create or modify `task_plan.md` (that's planning-with-files)
- Does not create or modify `progress.md` (that's planning-with-files)
- Does not create `SPEC.yaml` (that's tdd-sdd)
- Does not make routing decisions (that's triadev)

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create a parallel progress log | Use progress.md (planning-with-files) for human-readable logs |
| Schedule tasks without checking dependencies | Always validate DAG before scheduling |
| Ignore complexity scores | Score every task; execute low-complexity first |
| Skip cycle detection | Always check for circular dependencies |
| Schedule completed tasks | Filter out already-completed tasks before DAG analysis |

## Example

**Input (from task_plan.md):**
```markdown
## Phase 2: Implementation
- [ ] Create database schema (id: create-schema, complexity: 3)
- [ ] Implement user model (id: impl-user-model, deps: create-schema, complexity: 5)
- [ ] Implement auth middleware (id: impl-auth, deps: impl-user-model, complexity: 6)
- [ ] Write API endpoints (id: write-endpoints, deps: impl-user-model, complexity: 5)
- [ ] Integration tests (id: integration-tests, deps: impl-auth, write-endpoints, complexity: 7)
```

**Output (schedule):**
```
Batch 1: [create-schema]           complexity: 3
Batch 2: [impl-user-model]         complexity: 5  (depends: create-schema)
Batch 3: [impl-auth, write-endpoints]  complexity: 5-6  (parallel, both depend on impl-user-model)
Batch 4: [integration-tests]       complexity: 7  (depends: impl-auth, write-endpoints)
```
