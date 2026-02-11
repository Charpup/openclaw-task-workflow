"""
集成测试 - 端到端场景
"""
import pytest
from lib.task_scheduler import (
    TaskNode, TaskScheduler, DynamicTaskManager,
    DependencyAnalyzer, CircularDependencyError, TaskStatus
)


class TestE2EScenarios:
    """端到端场景测试"""
    
    def test_e2e_complete_workflow(self):
        """E2E-001: 完整任务调度流程"""
        # 5 个任务含依赖关系
        tasks = [
            TaskNode(id="setup", name="Setup", estimated_time="short", _complexity_score=2),
            TaskNode(id="config", name="Config", depends_on=["setup"], estimated_time="short", _complexity_score=3),
            TaskNode(id="build", name="Build", depends_on=["config"], estimated_time="medium", _complexity_score=5),
            TaskNode(id="test", name="Test", depends_on=["build"], estimated_time="long", _complexity_score=7),
            TaskNode(id="deploy", name="Deploy", depends_on=["test"], estimated_time="short", _complexity_score=4)
        ]
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        # 验证批次分组
        assert len(batches) == 5  # 线性依赖 = 5 个批次
        
        # 验证依赖顺序
        batch_ids = [[t.id for t in batch] for batch in batches]
        assert batch_ids[0] == ["setup"]
        assert batch_ids[1] == ["config"]
        assert batch_ids[2] == ["build"]
        assert batch_ids[3] == ["test"]
        assert batch_ids[4] == ["deploy"]
    
    def test_e2e_dynamic_insert(self):
        """E2E-002: 动态插入任务"""
        manager = DynamicTaskManager(max_batch_size=10)
        
        # 初始化 3 个任务
        manager.initialize([
            TaskNode(id="A", name="Task A", estimated_time="short", _complexity_score=1),
            TaskNode(id="B", name="Task B", depends_on=["A"], estimated_time="medium", _complexity_score=3),
            TaskNode(id="C", name="Task C", depends_on=["B"], estimated_time="short", _complexity_score=2)
        ])
        
        # 批次 1 执行
        batch1 = manager.get_next_batch()
        assert len(batch1) == 1
        assert batch1[0].id == "A"
        manager.mark_running("A")
        
        # 插入新任务 X（依赖 A）
        new_task = TaskNode(id="X", name="Task X", depends_on=["A"], estimated_time="short")
        new_task._complexity_score = 1.5
        manager.insert_task(new_task)
        
        # 批次 1 继续执行不中断
        assert "A" in manager.running_tasks
        
        # 完成 A
        manager.mark_completed("A")
        
        # 下一批应包含 B 和 X（都依赖 A，按复杂度排序）
        batch2 = manager.get_next_batch()
        batch2_ids = [t.id for t in batch2]
        assert "X" in batch2_ids
        assert "B" in batch2_ids
        assert batch2_ids.index("X") < batch2_ids.index("B")  # X 复杂度更低
    
    def test_e2e_circular_dependency_error(self):
        """E2E-003: 循环依赖检测"""
        tasks = [
            TaskNode(id="A", name="Task A", depends_on=["C"]),
            TaskNode(id="B", name="Task B", depends_on=["A"]),
            TaskNode(id="C", name="Task C", depends_on=["B"])
        ]
        
        with pytest.raises(CircularDependencyError) as exc_info:
            scheduler = TaskScheduler()
            scheduler.schedule_tasks(tasks)
        
        # 验证详细的循环路径
        error_msg = str(exc_info.value)
        assert "Circular dependency detected" in error_msg
    
    def test_e2e_parallel_with_dependencies(self):
        """复杂场景：并行 + 依赖混合"""
        #       A
        #      / \
        #     B   C
        #      \ /
        #       D
        tasks = [
            TaskNode(id="A", name="Task A", estimated_time="short", _complexity_score=2),
            TaskNode(id="B", name="Task B", depends_on=["A"], estimated_time="medium", _complexity_score=4),
            TaskNode(id="C", name="Task C", depends_on=["A"], estimated_time="short", _complexity_score=3),
            TaskNode(id="D", name="Task D", depends_on=["B", "C"], estimated_time="long", _complexity_score=6)
        ]
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        # Batch 1: A
        # Batch 2: C (3), B (4) - 按复杂度排序
        # Batch 3: D
        assert len(batches) == 3
        assert [t.id for t in batches[0]] == ["A"]
        assert set(t.id for t in batches[1]) == {"B", "C"}
        assert [t.id for t in batches[2]] == ["D"]
    
    def test_e2e_complexity_priority(self):
        """验证低复杂度优先策略"""
        # 多个无依赖任务
        tasks = [
            TaskNode(id="hard", name="Hard", estimated_time="long", _complexity_score=9),
            TaskNode(id="easy1", name="Easy 1", estimated_time="short", _complexity_score=2),
            TaskNode(id="medium", name="Medium", estimated_time="medium", _complexity_score=5),
            TaskNode(id="easy2", name="Easy 2", estimated_time="short", _complexity_score=1)
        ]
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        # 所有任务在同一批次（无依赖），按复杂度排序
        assert len(batches) == 1
        ordered_ids = [t.id for t in batches[0]]
        assert ordered_ids == ["easy2", "easy1", "medium", "hard"]
