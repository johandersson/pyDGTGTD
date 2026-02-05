#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.model.loader module.

Copyright (c) Johan Andersson, 2026
License: GPLv2+
"""

import pytest
from unittest.mock import Mock, patch

from wxgtd.model import loader


class TestSortObjectsByParent:
    """Tests for sort_objects_by_parent function."""
    
    def test_empty_list(self):
        """Test with empty list."""
        result = loader.sort_objects_by_parent([])
        assert result == []
    
    def test_single_root_object(self):
        """Test with single object with no parent."""
        objs = [{"_id": 1, "parent_id": 0, "title": "Root"}]
        result = loader.sort_objects_by_parent(objs)
        assert len(result) == 1
        assert result[0]["_id"] == 1
    
    def test_parent_child_order(self):
        """Test that parents come before children."""
        objs = [
            {"_id": 2, "parent_id": 1, "title": "Child"},
            {"_id": 1, "parent_id": 0, "title": "Parent"}
        ]
        result = loader.sort_objects_by_parent(objs)
        assert len(result) == 2
        assert result[0]["_id"] == 1  # Parent first
        assert result[1]["_id"] == 2  # Child second
    
    def test_multiple_roots(self):
        """Test with multiple root objects."""
        objs = [
            {"_id": 1, "parent_id": 0, "title": "Root1"},
            {"_id": 2, "parent_id": 0, "title": "Root2"},
            {"_id": 3, "parent_id": 0, "title": "Root3"}
        ]
        result = loader.sort_objects_by_parent(objs)
        assert len(result) == 3
        # All should have parent_id 0
        assert all(obj["parent_id"] == 0 for obj in result)
    
    def test_nested_hierarchy(self):
        """Test with nested parent-child relationships."""
        objs = [
            {"_id": 3, "parent_id": 2, "title": "Grandchild"},
            {"_id": 1, "parent_id": 0, "title": "Root"},
            {"_id": 2, "parent_id": 1, "title": "Child"}
        ]
        result = loader.sort_objects_by_parent(objs)
        assert len(result) == 3
        # Verify order: root -> child -> grandchild
        assert result[0]["_id"] == 1
        assert result[1]["_id"] == 2
        assert result[2]["_id"] == 3
    
    def test_multiple_children(self):
        """Test parent with multiple children."""
        objs = [
            {"_id": 1, "parent_id": 0, "title": "Parent"},
            {"_id": 2, "parent_id": 1, "title": "Child1"},
            {"_id": 3, "parent_id": 1, "title": "Child2"},
            {"_id": 4, "parent_id": 1, "title": "Child3"}
        ]
        result = loader.sort_objects_by_parent(objs)
        assert len(result) == 4
        # Parent should be first
        assert result[0]["_id"] == 1
        # All children should come after parent
        child_ids = {result[1]["_id"], result[2]["_id"], result[3]["_id"]}
        assert child_ids == {2, 3, 4}
    
    def test_orphaned_task_with_missing_parent(self):
        """Test handling of orphaned tasks with missing parents."""
        objs = [
            {"_id": 1, "parent_id": 0, "title": "Root", "note": ""},
            {"_id": 2, "parent_id": 999, "title": "Orphaned - parent missing", "note": ""},
            {"_id": 3, "parent_id": 1, "title": "Valid child", "note": ""}
        ]
        
        with patch('wxgtd.model.loader._LOG') as mock_log:
            result = loader.sort_objects_by_parent(objs)
            
            # Should process all objects
            assert len(result) == 3
            
            # Orphaned task should have parent_id changed to 0
            orphaned = next(obj for obj in result if obj["_id"] == 2)
            assert orphaned["parent_id"] == 0
            
            # Orphaned task should have a note about being orphaned
            assert "ORPHANED TASK" in orphaned["note"]
            assert "999" in orphaned["note"]  # Original parent ID should be mentioned
            
            # Should log warnings about orphaned objects
            assert mock_log.warning.called
            warning_calls = mock_log.warning.call_args_list
            assert any("orphaned" in str(call).lower() for call in warning_calls)
    
    def test_multiple_orphaned_tasks(self):
        """Test handling of multiple orphaned tasks."""
        objs = [
            {"_id": 1, "parent_id": 0, "title": "Root", "note": ""},
            {"_id": 2, "parent_id": 100, "title": "Orphan1", "note": ""},
            {"_id": 3, "parent_id": 100, "title": "Orphan2", "note": "Existing note"},
            {"_id": 4, "parent_id": 200, "title": "Orphan3", "note": ""},
            {"_id": 5, "parent_id": 1, "title": "Valid child", "note": ""}
        ]
        
        with patch('wxgtd.model.loader._LOG') as mock_log:
            result = loader.sort_objects_by_parent(objs)
            
            # All objects should be processed
            assert len(result) == 5
            
            # All orphaned tasks should have parent_id = 0
            orphaned_count = sum(1 for obj in result 
                               if obj["_id"] in [2, 3, 4] and obj["parent_id"] == 0)
            assert orphaned_count == 3
            
            # All orphaned tasks should have notes
            for obj in result:
                if obj["_id"] in [2, 3, 4]:
                    assert "ORPHANED TASK" in obj["note"]
            
            # Orphan with existing note should preserve it
            orphan3 = next(obj for obj in result if obj["_id"] == 3)
            assert "Existing note" in orphan3["note"]
            assert "ORPHANED TASK" in orphan3["note"]
            
            # Should log warning about 3 orphaned objects
            assert mock_log.warning.called
    
    def test_complex_hierarchy_with_orphans(self):
        """Test complex hierarchy with some orphaned branches."""
        objs = [
            {"_id": 1, "parent_id": 0, "title": "Root1", "note": ""},
            {"_id": 2, "parent_id": 1, "title": "Child of Root1", "note": ""},
            {"_id": 3, "parent_id": 2, "title": "Grandchild of Root1", "note": ""},
            {"_id": 10, "parent_id": 0, "title": "Root2", "note": ""},
            {"_id": 11, "parent_id": 10, "title": "Child of Root2", "note": ""},
            # Orphaned branch - parent 999 doesn't exist
            {"_id": 20, "parent_id": 999, "title": "Orphan parent", "note": ""},
            {"_id": 21, "parent_id": 20, "title": "Child of orphan", "note": ""},
            # Another orphan
            {"_id": 30, "parent_id": 888, "title": "Single orphan", "note": ""}
        ]
        
        with patch('wxgtd.model.loader._LOG') as mock_log:
            result = loader.sort_objects_by_parent(objs)
            
            # All objects should be processed
            assert len(result) == 8
            
            # Valid hierarchies should maintain their structure
            root1 = next(obj for obj in result if obj["_id"] == 1)
            assert root1["parent_id"] == 0
            
            # Orphaned objects should become root level
            orphan_parent = next(obj for obj in result if obj["_id"] == 20)
            assert orphan_parent["parent_id"] == 0
            assert "ORPHANED TASK" in orphan_parent["note"]
            
            single_orphan = next(obj for obj in result if obj["_id"] == 30)
            assert single_orphan["parent_id"] == 0
            assert "ORPHANED TASK" in single_orphan["note"]
            
            # Child of orphan also becomes orphaned (parent not in tree)
            # because parent 20 was orphaned, child 21 can't find it either
            child_of_orphan = next(obj for obj in result if obj["_id"] == 21)
            assert child_of_orphan["parent_id"] == 0
            assert "ORPHANED TASK" in child_of_orphan["note"]
    
    def test_circular_reference_prevention(self):
        """Test that circular references don't cause infinite loops."""
        # Note: Current implementation doesn't handle circular refs,
        # but orphaned handling prevents them from breaking everything
        objs = [
            {"_id": 1, "parent_id": 2, "title": "Task1", "note": ""},
            {"_id": 2, "parent_id": 1, "title": "Task2", "note": ""}
        ]
        
        with patch('wxgtd.model.loader._LOG') as mock_log:
            result = loader.sort_objects_by_parent(objs)
            
            # Both should be processed (as orphans since neither is root)
            assert len(result) == 2
            
            # Both should become root level to break the cycle
            assert all(obj["parent_id"] == 0 for obj in result)
            
            # Both should have orphan notes
            assert all("ORPHANED TASK" in obj["note"] for obj in result)
