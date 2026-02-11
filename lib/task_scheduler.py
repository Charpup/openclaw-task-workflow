"""
Task Workflow V2 - Core Implementation
智能任务调度系统
"""

from enum import Enum
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TimeEstimate(Enum):
    SHORT = "short"      # < 5 min
    MEDIUM = "medium"    # 5-15 min
    LONG = "long"        # > 15 min


@dataclass
class TaskNode:
    """任务节点 - 包含元数据、依赖、复杂度信息"""
    id: str
    name: str
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    estimated_time: str = "medium"
    tool_calls_estimate: int = 5
    decision_points: int = 0
    status: TaskStatus = TaskStatus.PENDING
    _complexity_score: Optional[float] = None
    
    def calculate_complexity(self) -> float:
        """计算任务复杂度评分 (1-10)"""
        time_scores = {"short": 1, "medium": 3, "long": 5}
        time_score = time_scores.get(self.estimated_time, 3)
        
        tool_score = min(self.tool_calls_estimate / 5, 3)
        decision_score = self.decision_points * 2
        
        total = time_score + tool_score + decision_score
        self._complexity_score = min(total, 10.0)
        return self._complexity_score
    
    @property
    def complexity_score(self) -> float:
        if self._complexity_score is None:
            return self.calculate_complexity()
        return self._complexity_score


class CircularDependencyError(Exception):
    """循环依赖错误"""
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        super().__init__(f"Circular dependency detected: {' -> '.join(cycle)}")


class DependencyAnalyzer:
    """依赖关系分析器"""
    
    @staticmethod
    def build_dependency_graph(tasks: List[TaskNode]) -> Dict[str, List[str]]:
        """构建依赖图并检测循环"""
        graph = defaultdict(list)
        in_degree = {t.id: 0 for t in tasks}
        task_map = {t.id: t for t in tasks}
        
        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id not in task_map:
                    raise ValueError(f"Dependency '{dep_id}' not found for task '{task.id}'")
                graph[dep_id].append(task.id)
                in_degree[task.id] += 1
        
        # 检测循环依赖
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for neighbor in graph[node_id]:
                if neighbor not in visited:
                    result = has_cycle(neighbor, path)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            path.pop()
            rec_stack.remove(node_id)
            return None
        
        for task_id in task_map:
            if task_id not in visited:
                cycle = has_cycle(task_id, [])
                if cycle:
                    raise CircularDependencyError(cycle)
        
        return dict(graph)


class TaskScheduler:
    """任务调度器 - 拓扑排序 + 复杂度优化"""
    
    def __init__(self, max_batch_size: int = 10):
        self.max_batch_size = max(5, min(max_batch_size, 20))  # 5-20 限制
    
    def schedule_tasks(self, tasks: List[TaskNode]) -> List[List[TaskNode]]:
        """将任务分组为可并行执行的批次"""
        if not tasks:
            return []
        
        # 构建依赖图
        graph = DependencyAnalyzer.build_dependency_graph(tasks)
        task_map = {t.id: t for t in tasks}
        
        # 计算入度
        in_degree = {t.id: 0 for t in tasks}
        for deps in graph.values():
            for dep_id in deps:
                in_degree[dep_id] += 1
        
        # 拓扑排序 + 批次分组
        batches = []
        remaining = set(t.id for t in tasks)
        
        while remaining:
            # 找出当前可执行的任务 (入度为 0)
            available = [tid for tid in remaining if in_degree[tid] == 0]
            
            if not available:
                # 还有剩余但没有可执行的 -> 循环依赖
                raise CircularDependencyError(list(remaining))
            
            # 按复杂度排序 (低 -> 高)
            available_tasks = [task_map[tid] for tid in available]
            available_tasks.sort(key=lambda t: t.complexity_score)
            
            # 分批处理
            batch = []
            for task in available_tasks:
                if len(batch) >= self.max_batch_size:
                    batches.append(batch)
                    batch = []
                batch.append(task)
                remaining.remove(task.id)
            
            if batch:
                batches.append(batch)
            
            # 更新入度
            for task in available_tasks:
                for next_id in graph.get(task.id, []):
                    in_degree[next_id] -= 1
        
        return batches


class DynamicTaskManager:
    """动态任务管理器 - 支持运行时插入"""
    
    def __init__(self, max_batch_size: int = 10):
        self.max_batch_size = max_batch_size
        self.scheduler = TaskScheduler(max_batch_size)
        self.running_tasks: Set[str] = set()
        self.pending_tasks: List[TaskNode] = []
        self.completed_tasks: Set[str] = set()
        self.all_tasks: Dict[str, TaskNode] = {}
    
    def initialize(self, tasks: List[TaskNode]):
        """初始化任务队列"""
        self.all_tasks = {t.id: t for t in tasks}
        self.pending_tasks = list(tasks)
    
    def insert_task(self, task: TaskNode) -> bool:
        """插入新任务到队列"""
        if task.id in self.all_tasks:
            return False
        
        self.all_tasks[task.id] = task
        
        # 检查依赖状态
        deps_completed = all(
            dep_id in self.completed_tasks 
            for dep_id in task.depends_on
        )
        deps_running = any(
            dep_id in self.running_tasks 
            for dep_id in task.depends_on
        )
        
        if deps_completed and not deps_running:
            # 依赖都已完成，可以立即执行
            task.status = TaskStatus.PENDING
        
        self.pending_tasks.append(task)
        
        # 重新排序
        self._reschedule_pending()
        return True
    
    def mark_running(self, task_id: str):
        """标记任务为执行中"""
        if task_id in self.all_tasks:
            self.all_tasks[task_id].status = TaskStatus.RUNNING
            self.running_tasks.add(task_id)
            self.pending_tasks = [t for t in self.pending_tasks if t.id != task_id]
    
    def mark_completed(self, task_id: str):
        """标记任务为已完成"""
        if task_id in self.all_tasks:
            self.all_tasks[task_id].status = TaskStatus.COMPLETED
            self.running_tasks.discard(task_id)
            self.completed_tasks.add(task_id)
            
            # 检查是否有等待此任务的 pending 任务
            self._reschedule_pending()
    
    def get_next_batch(self) -> List[TaskNode]:
        """获取下一批可执行的任务"""
        # 过滤出当前可执行且未完成的任务
        executable = []
        for task in self.pending_tasks:
            if task.status != TaskStatus.PENDING:
                continue
            deps_satisfied = all(
                dep_id in self.completed_tasks 
                for dep_id in task.depends_on
            )
            if deps_satisfied:
                executable.append(task)
        
        # 按复杂度排序并限制批次大小
        executable.sort(key=lambda t: t.complexity_score)
        return executable[:self.max_batch_size]
    
    def _reschedule_pending(self):
        """重新排序待执行队列"""
        # 按复杂度排序
        self.pending_tasks.sort(key=lambda t: t.complexity_score)
