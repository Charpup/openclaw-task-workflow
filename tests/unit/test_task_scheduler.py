"""
单元测试 - TaskScheduler
"""
import pytest
from lib.task_scheduler import TaskNode, TaskScheduler, CircularDependencyError


class TestTaskScheduler:
    """TaskScheduler 测试"""
    
    def test_simple_parallel(self):
        """TC-SCHED-001: 简单并行"""
        tasks = [
            TaskNode(id="A", name="Task A", estimated_time="medium"),
            TaskNode(id="B", name="Task B", estimated_time="short"),
            TaskNode(id="C", name="Task C", estimated_time="long")
        ]
        # 手动设置复杂度用于测试
        for t in tasks:
            t._complexity_score = {"A": 3, "B": 1, "C": 5}[t.id]
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        assert len(batches) == 1
        assert [t.id for t in batches[0]] == ["B", "A", "C"]  # 按复杂度排序
    
    def test_dependency_chain_with_parallel(self):
        """TC-SCHED-002: 依赖链 + 并行"""
        tasks = [
            TaskNode(id="A", name="Task A", depends_on=[], estimated_time="short"),
            TaskNode(id="B", name="Task B", depends_on=["A"], estimated_time="medium"),
            TaskNode(id="C", name="Task C", depends_on=[], estimated_time="short"),
            TaskNode(id="D", name="Task D", depends_on=["A"], estimated_time="medium")
        ]
        # 设置复杂度
        tasks[0]._complexity_score = 2  # A
        tasks[1]._complexity_score = 4  # B
        tasks[2]._complexity_score = 1  # C
        tasks[3]._complexity_score = 3  # D
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        assert len(batches) == 2
        # Batch 1: C (1) 和 A (2) - 无依赖，按复杂度排序
        batch1_ids = [t.id for t in batches[0]]
        assert "C" in batch1_ids
        assert "A" in batch1_ids
        assert batch1_ids.index("C") < batch1_ids.index("A")  # C 在 A 前面
        
        # Batch 2: D (3) 和 B (4) - 依赖 A
        batch2_ids = [t.id for t in batches[1]]
        assert "D" in batch2_ids
        assert "B" in batch2_ids
    
    def test_batch_size_limit(self):
        """TC-SCHED-003: 批次限制"""
        tasks = [
            TaskNode(id=f"T{i}", name=f"Task {i}", estimated_time="short")
            for i in range(15)
        ]
        for t in tasks:
            t._complexity_score = 1.0
        
        scheduler = TaskScheduler(max_batch_size=10)
        batches = scheduler.schedule_tasks(tasks)
        
        assert len(batches) == 2
        assert len(batches[0]) == 10
        assert len(batches[1]) == 5
    
    def test_empty_tasks(self):
        """测试空任务列表"""
        scheduler = TaskScheduler()
        batches = scheduler.schedule_tasks([])
        assert batches == []
    
    def test_batch_size_bounds(self):
        """测试批次大小边界"""
        scheduler = TaskScheduler(max_batch_size=3)
        assert scheduler.max_batch_size == 5  # 最小值 5
        
        scheduler = TaskScheduler(max_batch_size=25)
        assert scheduler.max_batch_size == 20  # 最大值 20
