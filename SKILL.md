---
name: task-workflow-v2
description: 智能任务调度系统 - 支持依赖分析、复杂度排序、动态插入的增强型任务工作流
author: Galatea
version: "2.0.0"
---

# Task Workflow V2

标准化任务执行流程，支持依赖分析、复杂度排序、动态任务插入。

## 改进点 (vs V1)

| 特性 | V1 | V2 |
|------|-----|-----|
| 依赖关系 | ❌ 无 | ✅ DAG 拓扑排序 |
| 复杂度排序 | ❌ 无 | ✅ 低复杂度优先 |
| 动态插入 | ❌ 无 | ✅ 执行中不中断 |
| 任务上限 | ❌ 无 | ✅ 默认 10，可配置 |
| 循环检测 | ❌ 无 | ✅ 自动检测 |

## 核心概念

### 任务复杂度 (Complexity)

综合评分 (1-10)：
```
复杂度 = 时间分 + 工具分 + 决策分

时间分: short=1, medium=3, long=5
工具分: min(工具数/5, 3)
决策分: 决策点数量 × 2
```

### 依赖关系 (Dependency)

使用 DAG (有向无环图) 模型：
```yaml
任务A:
  depends_on: []           # 无依赖

任务B:
  depends_on: ["任务A"]     # 依赖 A

任务C:
  depends_on: ["任务A", "任务B"]  # 多依赖
```

### 调度策略

1. **拓扑排序**: 保证依赖先执行
2. **复杂度优先**: 同层级按复杂度升序
3. **批次限制**: 单批最多 10 个任务
4. **动态插入**: 运行中任务不中断

## 使用方法

### 1. 定义任务

```python
from lib.task_scheduler import TaskNode

tasks = [
    TaskNode(
        id="research",
        name="技术调研",
        description="调研三个方案",
        estimated_time="medium",
        tool_calls_estimate=8,
        decision_points=1
    ),
    TaskNode(
        id="compare",
        name="方案对比",
        description="对比分析",
        depends_on=["research"],  # 依赖调研完成
        estimated_time="short",
        tool_calls_estimate=3,
        decision_points=2
    )
]
```

### 2. 调度任务

```python
from lib.task_scheduler import TaskScheduler

scheduler = TaskScheduler(max_batch_size=10)
batches = scheduler.schedule_tasks(tasks)

for i, batch in enumerate(batches):
    print(f"批次 {i+1}: {[t.name for t in batch]}")
```

### 3. 动态管理

```python
from lib.task_scheduler import DynamicTaskManager

manager = DynamicTaskManager()
manager.initialize(tasks)

# 获取下一批
batch = manager.get_next_batch()

# 标记执行中
for task in batch:
    manager.mark_running(task.id)

# 标记完成
manager.mark_completed(task.id)

# 动态插入新任务
new_task = TaskNode(id="extra", name="额外任务", depends_on=["research"])
manager.insert_task(new_task)
```

## 完整示例

```python
# 场景: 调研 A、B、C 三个方案

tasks = [
    # 第一批: 并行调研 (无依赖，按复杂度排序)
    TaskNode("research-a", "调研方案A", estimated_time="medium", tool_calls_estimate=6),
    TaskNode("research-b", "调研方案B", estimated_time="short", tool_calls_estimate=4),  # 先执行
    TaskNode("research-c", "调研方案C", estimated_time="long", tool_calls_estimate=10),  # 后执行
    
    # 第二批: 汇总对比 (依赖所有调研完成)
    TaskNode("summary", "汇总分析", 
             depends_on=["research-a", "research-b", "research-c"],
             estimated_time="medium", 
             decision_points=2)
]

scheduler = TaskScheduler()
batches = scheduler.schedule_tasks(tasks)

# 输出:
# 批次 1: [调研方案B, 调研方案A, 调研方案C]
# 批次 2: [汇总分析]
```

## 异常处理

| 场景 | 行为 |
|------|------|
| 循环依赖 | 抛出 `CircularDependencyError` |
| 缺失依赖 | 抛出 `ValueError` |
| 重复插入 | 返回 `False` |

## 配置选项

```python
scheduler = TaskScheduler(
    max_batch_size=10  # 范围: 5-20
)
```

## API 参考

### TaskNode
- `calculate_complexity()` → float: 计算复杂度
- `complexity_score` → float: 复杂度评分 (1-10)

### TaskScheduler
- `schedule_tasks(tasks)` → list[list[TaskNode]]: 返回批次分组

### DynamicTaskManager
- `initialize(tasks)`: 初始化任务队列
- `insert_task(task)` → bool: 插入新任务
- `get_next_batch()` → list[TaskNode]: 获取可执行任务
- `mark_running(task_id)`: 标记执行中
- `mark_completed(task_id)`: 标记完成

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 仅单元测试
pytest tests/unit -v

# 仅集成测试
pytest tests/integration -v
```

当前状态: **25/25 测试通过**

## 工作原理

```
输入任务列表
    ↓
构建依赖图 (DAG)
    ↓
拓扑排序 → 确定执行顺序
    ↓
按复杂度分组 → 批次划分
    ↓
输出: [[批次1], [批次2], ...]
```

---

*Workflow Version: 2.0.0*  
*Last Updated: 2026-02-10*
