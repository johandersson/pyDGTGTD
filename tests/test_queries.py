# -*- coding: utf-8 -*-
"""Tests for query building and params.

Copyright (c) Johan Andersson, 2026

This file is part of wxGTD
Licence: GPLv2+
"""

import unittest
import datetime
from unittest.mock import MagicMock, patch
from wxgtd.model import queries
from wxgtd.model import enums


class TestBuildQueryParams(unittest.TestCase):
	"""Test build_query_params function."""

	def test_query_all_task(self):
		"""Test building params for all tasks query."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		self.assertEqual(params['_query_group'], queries.QUERY_ALL_TASK)
		self.assertEqual(params['starred'], False)
		self.assertEqual(params['finished'], False)
		self.assertEqual(params['contexts'], [])
		self.assertEqual(params['folders'], [])
		self.assertEqual(params['statuses'], [])

	@patch('wxgtd.model.queries.AppConfig')
	def test_query_hotlist(self, mock_appconfig):
		"""Test building params for hotlist query."""
		# Mock AppConfig instance
		mock_config = MagicMock()
		mock_config.get.side_effect = lambda section, key, default=None: {
			('hotlist', 'cond'): True,
			('hotlist', 'due'): 0,
			('hotlist', 'priority'): 3,
			('hotlist', 'starred'): False,
			('hotlist', 'next_action'): False,
			('hotlist', 'started'): False,
		}.get((section, key), default)
		mock_appconfig.return_value = mock_config
		
		params = queries.build_query_params(
			queries.QUERY_HOTLIST, 0, None, "")
		self.assertEqual(params['_query_group'], queries.QUERY_HOTLIST)
		self.assertIn('filter_operator', params)
		self.assertIn('max_due_date', params)
		self.assertIn('min_priority', params)

	def test_query_today(self):
		"""Test building params for today query."""
		params = queries.build_query_params(
			queries.QUERY_TODAY, 0, None, "")
		self.assertEqual(params['_query_group'], queries.QUERY_TODAY)
		self.assertIsNotNone(params['max_due_date'])
		# Should be today's end
		max_due = params['max_due_date']
		self.assertEqual(max_due.hour, 23)
		self.assertEqual(max_due.minute, 59)

	def test_query_starred(self):
		"""Test building params for starred query."""
		params = queries.build_query_params(
			queries.QUERY_STARRED, 0, None, "")
		self.assertEqual(params['starred'], True)

	def test_query_basket(self):
		"""Test building params for basket query."""
		params = queries.build_query_params(
			queries.QUERY_BASKET, 0, None, "")
		self.assertEqual(params['contexts'], [None])
		self.assertEqual(params['statuses'], [0])
		self.assertEqual(params['goals'], [None])
		self.assertEqual(params['folders'], [None])
		self.assertEqual(params['tags'], [None])
		self.assertEqual(params['finished'], False)
		self.assertTrue(params.get('no_due_date'))

	def test_query_finished(self):
		"""Test building params for finished query."""
		params = queries.build_query_params(
			queries.QUERY_FINISHED, 0, None, "")
		self.assertEqual(params['finished'], True)

	def test_query_projects(self):
		"""Test building params for projects query."""
		params = queries.build_query_params(
			queries.QUERY_PROJECTS, 0, None, "")
		self.assertEqual(params['types'], [enums.TYPE_PROJECT])
		# With parent, should show all types
		params_with_parent = queries.build_query_params(
			queries.QUERY_PROJECTS, 0, "parent-uuid", "")
		self.assertIsNone(params_with_parent['types'])

	def test_query_checklists(self):
		"""Test building params for checklists query."""
		params = queries.build_query_params(
			queries.QUERY_CHECKLISTS, 0, None, "")
		self.assertEqual(params['types'], [enums.TYPE_CHECKLIST])
		# With parent, should show checklist and items
		params_with_parent = queries.build_query_params(
			queries.QUERY_CHECKLISTS, 0, "parent-uuid", "")
		self.assertEqual(params_with_parent['types'], 
			[enums.TYPE_CHECKLIST, enums.TYPE_CHECKLIST_ITEM])

	def test_query_future_alarms(self):
		"""Test building params for future alarms query."""
		params = queries.build_query_params(
			queries.QUERY_FUTURE_ALARMS, 0, None, "")
		self.assertTrue(params.get('active_alarm'))

	def test_query_trash(self):
		"""Test building params for trash query."""
		params = queries.build_query_params(
			queries.QUERY_TRASH, 0, None, "")
		self.assertTrue(params.get('deleted'))
		self.assertIsNone(params['hide_until'])
		self.assertIsNone(params['parent_uuid'])
		self.assertIsNone(params['finished'])

	def test_show_finished_option(self):
		"""Test OPT_SHOW_FINISHED option."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, queries.OPT_SHOW_FINISHED, None, "")
		self.assertIsNone(params['finished'])

	def test_show_subtasks_option(self):
		"""Test OPT_SHOW_SUBTASKS option."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, queries.OPT_SHOW_SUBTASKS, None, "")
		self.assertIsNone(params['parent_uuid'])

	def test_hide_until_option(self):
		"""Test OPT_HIDE_UNTIL option."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, queries.OPT_HIDE_UNTIL, None, "")
		self.assertTrue(params.get('hide_until'))

	def test_search_string(self):
		"""Test search string parameter."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "test search")
		self.assertEqual(params['search_str'], "test search")

	def test_parent_uuid(self):
		"""Test parent UUID parameter."""
		parent_uuid = "test-parent-uuid"
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, parent_uuid, "")
		self.assertEqual(params['parent_uuid'], parent_uuid)


class TestQueryParamsAppend(unittest.TestCase):
	"""Test query params append functions."""

	def test_append_contexts(self):
		"""Test appending contexts to params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		contexts = ['ctx1', 'ctx2', 'ctx3']
		queries.query_params_append_contexts(params, contexts)
		self.assertEqual(params['contexts'], contexts)

	def test_append_contexts_basket_ignored(self):
		"""Test appending contexts to basket query is ignored."""
		params = queries.build_query_params(
			queries.QUERY_BASKET, 0, None, "")
		original_contexts = params['contexts'].copy()
		queries.query_params_append_contexts(params, ['ctx1'])
		self.assertEqual(params['contexts'], original_contexts)

	def test_append_folders(self):
		"""Test appending folders to params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		folders = ['folder1', 'folder2']
		queries.query_params_append_folders(params, folders)
		self.assertEqual(params['folders'], folders)

	def test_append_goals(self):
		"""Test appending goals to params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		goals = ['goal1', 'goal2']
		queries.query_params_append_goals(params, goals)
		self.assertEqual(params['goals'], goals)

	def test_append_statuses(self):
		"""Test appending statuses to params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		statuses = [1, 2, 3]
		queries.query_params_append_statuses(params, statuses)
		self.assertEqual(params['statuses'], statuses)

	def test_append_tags(self):
		"""Test appending tags to params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		tags = ['tag1', 'tag2']
		queries.query_params_append_tags(params, tags)
		self.assertEqual(params['tags'], tags)

	def test_multiple_appends(self):
		"""Test multiple appends to same params."""
		params = queries.build_query_params(
			queries.QUERY_ALL_TASK, 0, None, "")
		queries.query_params_append_contexts(params, ['ctx1'])
		queries.query_params_append_contexts(params, ['ctx2'])
		queries.query_params_append_folders(params, ['folder1'])
		queries.query_params_append_statuses(params, [1, 2])
		
		self.assertEqual(params['contexts'], ['ctx1', 'ctx2'])
		self.assertEqual(params['folders'], ['folder1'])
		self.assertEqual(params['statuses'], [1, 2])


class TestQueryConstants(unittest.TestCase):
	"""Test query constants are properly defined."""

	def test_query_constants_are_unique(self):
		"""Test all query constants have unique values."""
		constants = [
			queries.QUERY_ALL_TASK,
			queries.QUERY_HOTLIST,
			queries.QUERY_TODAY,
			queries.QUERY_STARRED,
			queries.QUERY_BASKET,
			queries.QUERY_FINISHED,
			queries.QUERY_PROJECTS,
			queries.QUERY_CHECKLISTS,
			queries.QUERY_FUTURE_ALARMS,
			queries.QUERY_TRASH
		]
		self.assertEqual(len(constants), len(set(constants)))

	def test_option_constants_are_powers_of_two(self):
		"""Test option constants can be combined with bitwise OR."""
		self.assertEqual(queries.OPT_SHOW_FINISHED, 1)
		self.assertEqual(queries.OPT_SHOW_SUBTASKS, 2)
		self.assertEqual(queries.OPT_HIDE_UNTIL, 4)
		# Test bitwise combination
		combined = queries.OPT_SHOW_FINISHED | queries.OPT_SHOW_SUBTASKS
		self.assertEqual(combined, 3)


if __name__ == '__main__':
	unittest.main()
