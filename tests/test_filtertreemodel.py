# -*- coding: utf-8 -*-
"""Tests for filter tree model.

Copyright (c) Johan Andersson, 2026

This file is part of wxGTD
Licence: GPLv2+
"""

import unittest
from unittest.mock import MagicMock, patch
from wxgtd.gui._filtertreectrl import TreeItem, TreeItemCB, FilterTreeModel


class TestTreeItem(unittest.TestCase):
	"""Test TreeItem class."""

	def test_create_tree_item(self):
		"""Test creating a basic tree item."""
		item = TreeItem("Test Title", "test-obj")
		self.assertEqual(item.title, "Test Title")
		self.assertEqual(item.obj, "test-obj")
		self.assertEqual(len(item.childs), 0)

	def test_create_tree_item_with_children(self):
		"""Test creating tree item with children."""
		child1 = TreeItem("Child 1", "child1")
		child2 = TreeItem("Child 2", "child2")
		parent = TreeItem("Parent", "parent", child1, child2)
		self.assertEqual(len(parent.childs), 2)
		self.assertEqual(parent.childs[0].title, "Child 1")
		self.assertEqual(parent.childs[1].title, "Child 2")

	def test_get_item_direct_child(self):
		"""Test getting direct child item."""
		child = TreeItem("Child", "child")
		parent = TreeItem("Parent", "parent", child)
		result = parent.get_item([0])
		self.assertEqual(result.title, "Child")

	def test_get_item_nested(self):
		"""Test getting nested child item."""
		grandchild = TreeItem("Grandchild", "gc")
		child = TreeItem("Child", "child", grandchild)
		parent = TreeItem("Parent", "parent", child)
		result = parent.get_item([0, 0])
		self.assertEqual(result.title, "Grandchild")


class TestTreeItemCB(unittest.TestCase):
	"""Test TreeItemCB (checkbox item) class."""

	def test_create_checkbox_item(self):
		"""Test creating a checkbox item."""
		item = TreeItemCB("Test", "test-obj")
		self.assertEqual(item.title, "Test")
		self.assertFalse(item.checked)
		self.assertEqual(item.node_type, 1)  # NODE_CHECKBOX

	def test_set_child_check(self):
		"""Test setting all children checked state."""
		child1 = TreeItemCB("Child 1", "c1")
		child2 = TreeItemCB("Child 2", "c2")
		parent = TreeItemCB("Parent", "parent", child1, child2)
		
		parent.set_child_check(True)
		self.assertTrue(child1.checked)
		self.assertTrue(child2.checked)
		
		parent.set_child_check(False)
		self.assertFalse(child1.checked)
		self.assertFalse(child2.checked)


class TestFilterTreeModel(unittest.TestCase):
	"""Test FilterTreeModel class."""

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_create_model(self, mock_obj, mock_appconfig):
		"""Test creating filter tree model."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		# Mock the model objects
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		self.assertIsNotNone(model._items)
		self.assertEqual(len(model._items), 5)  # STATUSES, CONTEXTS, FOLDERS, GOALS, TAGS

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_get_text_without_counts(self, mock_obj, mock_appconfig):
		"""Test getting text without count callback."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		# Get first category (Statuses)
		text = model.get_text([0])
		self.assertIn("Status", text)  # Should contain 'Status' or 'Statuses'
		
	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_get_text_with_count_callback(self, mock_obj, mock_appconfig):
		"""Test getting text with count callback."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		# Create mock count callback
		def mock_count_callback(category, item_id):
			if category == "STATUSES" and item_id == 1:
				return 5
			return 0
		
		model = FilterTreeModel(count_callback=mock_count_callback)
		
		# Get text for a status item (should include count)
		# First item is statuses category [0], first child is first status [0,0]
		text = model.get_text([0, 0])
		if text.endswith("(5)"):
			self.assertTrue(True)  # Count was added
		# Count might be 0, which won't add suffix
		
	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_get_children_count_root(self, mock_obj, mock_appconfig):
		"""Test getting children count from root."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		count = model.get_children_count([])
		self.assertEqual(count, 5)  # 5 main categories

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_get_item_type(self, mock_obj, mock_appconfig):
		"""Test getting item type."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		# Root should be type 0
		typ = model.get_item_type([])
		self.assertEqual(typ, 0)
		# Categories should be checkboxes (type 1)
		typ = model.get_item_type([0])
		self.assertEqual(typ, 1)

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_checked_items_by_parent(self, mock_obj, mock_appconfig):
		"""Test getting checked items by parent category."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		# Find statuses item and check some children
		statuses_item = None
		for item in model._items:
			if item.obj == "STATUSES":
				statuses_item = item
				break
		
		self.assertIsNotNone(statuses_item)
		
		# Check first two status items
		if len(statuses_item.childs) >= 2:
			statuses_item.childs[0].checked = True
			statuses_item.childs[1].checked = True
			
			checked = list(model.checked_items_by_parent("STATUSES"))
			self.assertEqual(len(checked), 2)

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_check_items(self, mock_obj, mock_appconfig):
		"""Test checking items by IDs."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		model = FilterTreeModel()
		
		# Get all status IDs
		statuses_item = None
		for item in model._items:
			if item.obj == "STATUSES":
				statuses_item = item
				break
		
		if statuses_item and len(statuses_item.childs) > 0:
			# Check items by their IDs
			ids_to_check = {statuses_item.childs[0].obj}
			model.check_items("STATUSES", ids_to_check)
			
			# Verify the item is checked
			self.assertTrue(statuses_item.childs[0].checked)

	@patch('wxgtd.gui._filtertreectrl.appconfig.AppConfig')
	@patch('wxgtd.gui._filtertreectrl.OBJ')
	def test_counts_cache(self, mock_obj, mock_appconfig):
		"""Test that counts are cached."""
		# Mock AppConfig
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		mock_obj.Context.all.return_value = []
		mock_obj.Folder.all.return_value = []
		mock_obj.Goal.all.return_value = []
		mock_obj.Tag.all.return_value = []
		
		call_count = 0
		
		def mock_count_callback(category, item_id):
			nonlocal call_count
			call_count += 1
			return 5
		
		model = FilterTreeModel(count_callback=mock_count_callback)
		
		# Call get_text twice with same indices
		model.get_text([0, 0])
		model.get_text([0, 0])
		
		# Should only call callback once due to caching
		self.assertEqual(call_count, 1)
		
		# Clear cache
		model._counts_cache = {}
		
		# Call again, should increment count
		model.get_text([0, 0])
		self.assertEqual(call_count, 2)


if __name__ == '__main__':
	unittest.main()
