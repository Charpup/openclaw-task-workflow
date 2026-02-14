"""
Task Persistence Manager V3.1
Enhanced V3 with auto-numbering from v2.1.0
"""

from lib.task_persistence import TaskPersistenceManager, TaskRecord
from lib.task_index_manager import TaskIndexManager, format_task_id
from typing import Optional


class TaskPersistenceManagerV31(TaskPersistenceManager):
    """
    V3.1 Enhanced Persistence Manager
    
    Adds:
    - Auto-numbering via TaskIndexManager
    - Progress monitoring hooks
    """
    
    def __init__(self, backlog_dir: Optional[str] = None, index_file: Optional[str] = None):
        super().__init__(backlog_dir)
        self.index_manager = TaskIndexManager(index_file)
        self.index_manager.init()
    
    def create_task(self, name: str, **kwargs) -> TaskRecord:
        """
        Create task with auto-numbering.
        
        Overrides V3 create_task to add:
        1. Auto-generated task ID (task_001, task_002...)
        2. Registration in index
        """
        # Get auto-numbered ID
        task_number = self.index_manager.get_next_id()
        task_id = format_task_id(task_number)
        
        # Create task record
        task = TaskRecord(
            id=task_id,
            name=name,
            **kwargs
        )
        
        # Register in index
        self.index_manager.register_task({
            "id": task_id,
            "name": name,
            "status": task.status,
            "complexity_score": task.complexity_score
        })
        
        # Add to daily file (V3 behavior)
        self.add_task(task)
        
        return task
    
    def get_task_by_number(self, number: int) -> Optional[TaskRecord]:
        """Get task by number (001 => task_001)"""
        task_id = format_task_id(number)
        return self.get_task_by_id(task_id)
    
    def get_task_by_id(self, task_id: str) -> Optional[TaskRecord]:
        """Get task by ID from current tasks"""
        tasks = self.get_current_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None


# Convenience function
def create_v31_manager():
    """Factory function for V3.1 manager"""
    return TaskPersistenceManagerV31()
