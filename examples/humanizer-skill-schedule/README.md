# Example: humanizer-skill schedule (GOLD — real completed run)

## What this is

A real completed task-workflow run from `projects/humanizer-skill/` (March 2026).
A 21-task skill build that went planning → scheduling → implementation → PR merged.

Inputs are the **verbatim** `task_plan.md` from the project. Outputs are what
task-workflow's DAG analysis produces from that plan.

## Why GOLD

- ✅ Real completed project (PR blader/humanizer#94 landed)
- ✅ 20 of 21 tasks completed — realistic in-flight state
- ✅ Mix of task complexities (1–7), mix of dependency shapes (fan-out, fan-in, parallel)
- ✅ Shows both `tasks_extracted` (from handoff.json) and `batches` (scheduled output)
- ✅ Demonstrates within-batch complexity ordering (lowest complexity first)

## Files

| File | Role |
|------|------|
| `input-task_plan.md` | Input to task-workflow (extracted from project) |
| `output-schedule.json` | task-workflow output (batches + metadata) |
| `output-handoff-snippet.json` | How this schedule lives inside triadev-handoff.json |

## Characteristic lessons

1. **Complexity ordering within a batch**: Batch 1 contains 4 independent tasks
   (T1, T2, T6, T16). They're ordered T1(1) → T2(1) → T16(1) → T6(4), ascending
   by complexity as per scheduler rule.

2. **Fan-out from T7**: T7 (merge 32 patterns, complexity 7) is the single-point
   dependency for 5 downstream tasks (T8–T12). Those 5 run in parallel after T7.

3. **Fan-in to T13**: T13 (SKILL.md) depends on all 5 reference files (T8–T12).
   The scheduler correctly waits for the entire batch to complete before running T13.

4. **Linear tail (T17 → T21)**: Deployment phase is inherently sequential. No
   parallelization possible.

5. **Standalone-style output**: This example uses task-workflow without triadev.
   Output is formatted text + JSON, not written to triadev-handoff.json. The final
   file shows how the same schedule maps into handoff.json if triadev orchestrates.

## What would make this NOT an ideal reference

- Task complexity scores were assigned by the author, not derived from code
- No cross-session daily-file migration shown (project completed in one week,
  mostly in 2-3 sessions — no CST 00:00 migrations occurred)
- For daily-file migration example, see `references/file-format.md` (spec only)
