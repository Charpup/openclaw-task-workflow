"""
单元测试 - DynamicTaskManager
"""
import pytest
from lib.task_scheduler import TaskNode, DynamicTaskManager, TaskStatus


class TestDynamicTaskManager:
    """DynamicTaskManager 测试"""
    
    def test_insert_to_pending(self):
        """TC-DYN-001: 插入到待执行队列"""
        manager = DynamicTaskManager()
        manager.initialize([
            TaskNode(id="A", name="Task A", estimated_time="medium", _complexity_score=3),
            TaskNode(id="B", name="Task B", estimated_time="long", _complexity_score=5)
        ])
        
        # 插入复杂度为 2 的新任务
        new_task = TaskNode(id="C", name="Task C", estimated_time="short")
        new_task._complexity_score = 2
        
        result = manager.insert_task(new_task)
        assert result is True
        
        pending_ids = [t.id for t in manager.pending_tasks]
        assert pending_ids.index("C") < pending_ids.index("A")  # C 排在 A 前面
    
    def test_insert_with_running_dependency(self):
        """TC-DYN-002: 依赖运行中任务"""
        manager = DynamicTaskManager()
        manager.initialize([
            TaskNode(id="A", name="Task A", estimated_time="short")
        ])
        
        # 标记 A 为运行中
        manager.mark_running("A")
        
        # 插入依赖 A 的任务
        new_task = TaskNode(id="B", name="Task B", depends_on=["A"])
        result = manager.insert_task(new_task)
        
        assert result is True
        assert "B" in [t.id for t in manager.pending_tasks]
        assert manager.get_next_batch() == []  # B 还不能执行
    
    def test_insert_with_completed_dependency(self):
        """TC-DYN-003: 依赖已完成任务"""
        manager = DynamicTaskManager()
        manager.initialize([
            TaskNode(id="A", name="Task A", estimated_time="short")
        ])
        
        # 标记 A 为已完成
        manager.mark_completed("A")
        
        # 插入依赖 A 的任务
        new_task = TaskNode(id="B", name="Task B", depends_on=["A"])
        result = manager.insert_task(new_task)
        
        assert result is True
        next_batch = manager.get_next_batch()
        assert len(next_batch) == 1
        assert next_batch[0].id == "B"
    
    def test_duplicate_insert_fails(self):
        """测试重复插入失败"""
        manager = DynamicTaskManager()
        task = TaskNode(id="A", name="Task A")
        manager.initialize([task])
        
        result = manager.insert_task(task)
        assert result is False
    
    def test_mark_running_and_completed(self):
        """测试状态转换"""
        manager = DynamicTaskManager()
        manager.initialize([
            TaskNode(id="A", name="Task A", estimated_time="short")
        ])
        
        assert "A" in [t.id for t in manager.pending_tasks]
        
        manager.mark_running("A")
        assert "A" in manager.running_tasks
        assert "A" not in [t.id for t in manager.pending_tasks]
        
        manager.mark_completed("A")
        assert "A" in manager.completed_tasks
        assert "A" not in manager.running_tasks
