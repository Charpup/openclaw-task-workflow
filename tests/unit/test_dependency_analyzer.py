"""
单元测试 - DependencyAnalyzer
"""
import pytest
from lib.task_scheduler import TaskNode, DependencyAnalyzer, CircularDependencyError


class TestDependencyAnalyzer:
    """DependencyAnalyzer 测试"""
    
    def test_no_dependencies(self):
        """TC-DEPS-001: 无依赖任务"""
        tasks = [
            TaskNode(id="A", name="Task A"),
            TaskNode(id="B", name="Task B")
        ]
        graph = DependencyAnalyzer.build_dependency_graph(tasks)
        assert graph["A"] == []
        assert graph["B"] == []
    
    def test_linear_dependency(self):
        """TC-DEPS-002: 线性依赖 A->B->C"""
        tasks = [
            TaskNode(id="A", name="Task A", depends_on=[]),
            TaskNode(id="B", name="Task B", depends_on=["A"]),
            TaskNode(id="C", name="Task C", depends_on=["B"])
        ]
        graph = DependencyAnalyzer.build_dependency_graph(tasks)
        assert graph["A"] == ["B"]
        assert graph["B"] == ["C"]
        assert graph["C"] == []
    
    def test_circular_dependency_detection(self):
        """TC-DEPS-003: 循环依赖检测"""
        tasks = [
            TaskNode(id="A", name="Task A", depends_on=["C"]),
            TaskNode(id="B", name="Task B", depends_on=["A"]),
            TaskNode(id="C", name="Task C", depends_on=["B"])
        ]
        with pytest.raises(CircularDependencyError) as exc_info:
            DependencyAnalyzer.build_dependency_graph(tasks)
        assert "A" in str(exc_info.value)
        assert "B" in str(exc_info.value)
        assert "C" in str(exc_info.value)
    
    def test_missing_dependency(self):
        """测试缺失依赖"""
        tasks = [
            TaskNode(id="A", name="Task A", depends_on=["Missing"])
        ]
        with pytest.raises(ValueError) as exc_info:
            DependencyAnalyzer.build_dependency_graph(tasks)
        assert "Missing" in str(exc_info.value)
    
    def test_diamond_dependency(self):
        """测试菱形依赖 A->B, A->C, B->D, C->D"""
        tasks = [
            TaskNode(id="A", name="Task A"),
            TaskNode(id="B", name="Task B", depends_on=["A"]),
            TaskNode(id="C", name="Task C", depends_on=["A"]),
            TaskNode(id="D", name="Task D", depends_on=["B", "C"])
        ]
        graph = DependencyAnalyzer.build_dependency_graph(tasks)
        assert set(graph["A"]) == {"B", "C"}
        assert graph["B"] == ["D"]
        assert graph["C"] == ["D"]
