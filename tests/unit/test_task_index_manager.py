"""
Unit tests for TaskIndexManager (V3.1.0)
TDD: RED phase - tests should fail initially
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

# Import will fail initially (module doesn't exist yet)
# This is RED phase
from lib.task_index_manager import TaskIndexManager, TaskIndex


class TestTaskIndexManager:
    """TaskIndexManager test suite"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create TaskIndexManager instance"""
        index_file = Path(temp_dir) / "test_index.json"
        return TaskIndexManager(index_file=str(index_file))
    
    def test_initialization_creates_index(self, manager, temp_dir):
        """Test that initialization creates index file"""
        manager.init()
        assert manager.index_file.exists()
    
    def test_get_next_id_first_task(self, manager):
        """Test: First task gets ID 1"""
        manager.init()
        next_id = manager.get_next_id()
        assert next_id == 1
    
    def test_get_next_id_sequential(self, manager):
        """Test: IDs are sequential"""
        manager.init()
        assert manager.get_next_id() == 1
        assert manager.get_next_id() == 2
        assert manager.get_next_id() == 3
    
    def test_register_task(self, manager):
        """Test: Registering a task"""
        manager.init()
        
        task = {
            "id": "task_001",
            "name": "Test Task",
            "status": "pending"
        }
        
        manager.register_task(task)
        
        # Verify task is in index
        assert manager.get_task("task_001")["name"] == "Test Task"
    
    def test_list_active_excludes_completed(self, manager):
        """Test: list_active returns only non-completed tasks"""
        manager.init()
        
        # Add pending task
        manager.register_task({
            "id": "task_001",
            "name": "Pending Task",
            "status": "pending"
        })
        
        # Add completed task
        manager.register_task({
            "id": "task_002",
            "name": "Completed Task",
            "status": "completed"
        })
        
        active = manager.list_active()
        
        assert len(active) == 1
        assert active[0]["id"] == "task_001"
    
    def test_persistence(self, temp_dir):
        """Test: Index persists across instances"""
        index_file = Path(temp_dir) / "persist_test.json"
        
        # First instance
        manager1 = TaskIndexManager(index_file=str(index_file))
        manager1.init()
        manager1.register_task({
            "id": "task_001",
            "name": "Persistent Task",
            "status": "pending"
        })
        
        # Second instance - should load same index
        manager2 = TaskIndexManager(index_file=str(index_file))
        manager2.init()
        
        assert manager2.get_task("task_001")["name"] == "Persistent Task"


class TestTaskIndex:
    """TaskIndex data class tests"""
    
    def test_task_index_creation(self):
        """Test TaskIndex dataclass"""
        index = TaskIndex(
            version="1.0.0",
            last_task_id=0,
            active_tasks=[],
            archived_tasks=[]
        )
        
        assert index.version == "1.0.0"
        assert index.last_task_id == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
