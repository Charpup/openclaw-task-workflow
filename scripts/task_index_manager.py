"""
Task Index Manager - V3.1.0
Auto-numbering and task indexing system
Ported from v2.1.0 Node.js to Python
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class TaskIndex:
    """Task index data structure"""
    version: str = "1.0.0"
    last_task_id: int = 0
    active_tasks: List[Dict[str, Any]] = field(default_factory=list)
    archived_tasks: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskIndex':
        return cls(**data)


class TaskIndexManager:
    """
    Manages task indexing with auto-numbering.
    
    Features:
    - Auto-generates sequential task IDs (001, 002...)
    - Maintains active and archived task lists
    - Persists to JSON file
    """
    
    def __init__(self, index_file: Optional[str] = None):
        self.index_file = Path(index_file) if index_file else Path("task_backlog/index.json")
        self._index: Optional[TaskIndex] = None
    
    def init(self) -> None:
        """Initialize or load existing index"""
        if self.index_file.exists():
            self._load_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self) -> None:
        """Create new empty index"""
        self._index = TaskIndex()
        self._save_index()
    
    def _load_index(self) -> None:
        """Load index from file"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._index = TaskIndex.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            # Corrupted index, create new
            self._create_new_index()
    
    def _save_index(self) -> None:
        """Save index to file"""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self._index.updated_at = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self._index.to_dict(), f, indent=2)
    
    def get_next_id(self) -> int:
        """Get next sequential task ID"""
        if self._index is None:
            raise RuntimeError("Index not initialized. Call init() first.")
        
        self._index.last_task_id += 1
        self._save_index()
        return self._index.last_task_id
    
    def register_task(self, task: Dict[str, Any]) -> None:
        """Register a task in the index"""
        if self._index is None:
            raise RuntimeError("Index not initialized. Call init() first.")
        
        # Check if task already exists
        existing = self.get_task(task.get("id"))
        if existing:
            # Update existing
            for i, t in enumerate(self._index.active_tasks):
                if t.get("id") == task["id"]:
                    self._index.active_tasks[i] = task
                    break
        else:
            # Add new
            self._index.active_tasks.append(task)
        
        self._save_index()
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        if self._index is None:
            return None
        
        for task in self._index.active_tasks:
            if task.get("id") == task_id:
                return task
        
        # Also check archived
        for task in self._index.archived_tasks:
            if task.get("id") == task_id:
                return task
        
        return None
    
    def list_active(self) -> List[Dict[str, Any]]:
        """List all non-completed active tasks"""
        if self._index is None:
            return []
        
        return [
            task for task in self._index.active_tasks
            if task.get("status") != "completed"
        ]
    
    def archive_task(self, task_id: str) -> bool:
        """Move task to archive"""
        if self._index is None:
            return False
        
        for i, task in enumerate(self._index.active_tasks):
            if task.get("id") == task_id:
                task["archived_at"] = datetime.now().isoformat()
                self._index.archived_tasks.append(task)
                self._index.active_tasks.pop(i)
                self._save_index()
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get index statistics"""
        if self._index is None:
            return {"total": 0, "active": 0, "archived": 0}
        
        return {
            "total": self._index.last_task_id,
            "active": len(self._index.active_tasks),
            "archived": len(self._index.archived_tasks)
        }


# Convenience function for V3 integration
def format_task_id(number: int) -> str:
    """Format number as task ID (001, 002...)"""
    return f"task_{number:03d}"
