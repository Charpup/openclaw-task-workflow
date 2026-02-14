"""
V3.1 Integration Tests
"""

import pytest
import tempfile
from pathlib import Path

from lib.task_index_manager import TaskIndexManager, format_task_id
from lib.subagent_monitor import SubagentProgressMonitor
from lib.task_persistence_v31 import TaskPersistenceManagerV31


class TestV31Integration:
    """V3.1 End-to-end integration tests"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_create_task_with_auto_numbering(self, temp_dir):
        """Test: Create task gets auto-numbered ID"""
        index_file = Path(temp_dir) / "index.json"
        manager = TaskPersistenceManagerV31(
            backlog_dir=temp_dir,
            index_file=str(index_file)
        )
        
        task = manager.create_task("Test Task")
        
        assert task.id == "task_001"
        assert task.name == "Test Task"
    
    def test_sequential_numbering(self, temp_dir):
        """Test: Multiple tasks get sequential IDs"""
        index_file = Path(temp_dir) / "index.json"
        manager = TaskPersistenceManagerV31(
            backlog_dir=temp_dir,
            index_file=str(index_file)
        )
        
        task1 = manager.create_task("Task 1")
        task2 = manager.create_task("Task 2")
        task3 = manager.create_task("Task 3")
        
        assert task1.id == "task_001"
        assert task2.id == "task_002"
        assert task3.id == "task_003"
    
    def test_format_task_id(self):
        """Test: ID formatting"""
        assert format_task_id(1) == "task_001"
        assert format_task_id(10) == "task_010"
        assert format_task_id(100) == "task_100"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
