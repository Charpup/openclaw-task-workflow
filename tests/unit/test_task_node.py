"""
单元测试 - TaskNode
"""
import pytest
from lib.task_scheduler import TaskNode, TaskStatus


class TestTaskNode:
    """TaskNode 测试"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        task = TaskNode(id="test-1", name="Test Task")
        assert task.id == "test-1"
        assert task.name == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.depends_on == []
    
    def test_complexity_short_simple(self):
        """TC-COMP-001: 简单任务"""
        task = TaskNode(
            id="simple",
            name="Simple Task",
            estimated_time="short",
            tool_calls_estimate=2,
            decision_points=0
        )
        score = task.calculate_complexity()
        assert 1.0 <= score <= 2.0
        assert score == pytest.approx(1.4, rel=0.1)
    
    def test_complexity_medium(self):
        """TC-COMP-002: 中等复杂度"""
        task = TaskNode(
            id="medium",
            name="Medium Task",
            estimated_time="medium",
            tool_calls_estimate=8,
            decision_points=2
        )
        score = task.calculate_complexity()
        # medium(3) + tools(8/5=1.6) + decisions(2*2=4) = 8.6
        assert 8.0 <= score <= 9.0
        assert score == pytest.approx(8.6, rel=0.1)
    
    def test_complexity_long_complex(self):
        """TC-COMP-003: 复杂任务"""
        task = TaskNode(
            id="complex",
            name="Complex Task",
            estimated_time="long",
            tool_calls_estimate=15,
            decision_points=5
        )
        score = task.calculate_complexity()
        assert score == 10.0  # 被限制到 10
    
    def test_complexity_caching(self):
        """测试复杂度缓存"""
        task = TaskNode(id="cache", name="Cache Test", estimated_time="short")
        score1 = task.complexity_score
        score2 = task.complexity_score
        assert score1 == score2
