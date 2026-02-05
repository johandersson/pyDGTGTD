# -*- coding: utf-8 -*-
""" Project List Panel - displays projects categorized by action status.

Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Johan Andersson"
__copyright__ = "Copyright (c) Johan Andersson, 2025"
__version__ = "2025-02-05"

import gettext
import logging

import wx

from wxgtd.model import objects as OBJ
from wxgtd.gui import _tasklistctrl as TLC

_ = gettext.gettext
_LOG = logging.getLogger(__name__)


class ProjectListPanel(wx.Panel):
	""" Panel that displays projects in two categories:
	- Projects with actions (have tasks) - with tasks shown indented below
	- Projects with no tasks (empty projects)
	"""

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
		self._session = None
		self._setup_ui()

	def _setup_ui(self):
		""" Create the UI components. """
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		# Title
		title = wx.StaticText(self, -1, _("Project List"))
		font = title.GetFont()
		font.PointSize += 2
		font = font.Bold()
		title.SetFont(font)
		main_sizer.Add(title, 0, wx.ALL, 10)

		# Projects with actions section
		label_with_actions = wx.StaticText(self, -1, 
			_("Projects with Actions"))
		font = label_with_actions.GetFont()
		font = font.Bold()
		label_with_actions.SetFont(font)
		main_sizer.Add(label_with_actions, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

		# Use TaskListControl for projects with actions
		self._list_with_actions = TLC.TaskListControl(self)
		main_sizer.Add(self._list_with_actions, 1, 
			wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		# Projects with no tasks section
		label_no_tasks = wx.StaticText(self, -1, 
			_("Projects with No Tasks"))
		font = label_no_tasks.GetFont()
		font = font.Bold()
		label_no_tasks.SetFont(font)
		main_sizer.Add(label_no_tasks, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

		# Use TaskListControl for projects without tasks
		self._list_no_tasks = TLC.TaskListControl(self)
		main_sizer.Add(self._list_no_tasks, 1, 
			wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		self.SetSizer(main_sizer)

		# Bind double-click events
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated_with_tasks,
			self._list_with_actions)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated_no_tasks,
			self._list_no_tasks)

	def refresh(self, session=None):
		""" Refresh the project list from the database. """
		self._session = session or OBJ.Session()
		
		# Clear existing items
		self._list_with_actions.DeleteAllItems()
		self._list_no_tasks.DeleteAllItems()

		# Get all projects (not completed, not deleted)
		all_projects = OBJ.Task.all_projects().all()
		
		projects_with_actions = []
		projects_no_tasks = []

		# Categorize projects
		for project in all_projects:
			if project.completed or project.deleted:
				continue  # Skip completed and deleted projects
			
			# Count children (tasks) - using cached property
			child_count = project.child_count
			
			if child_count > 0:
				projects_with_actions.append(project)
			else:
				projects_no_tasks.append(project)

		# Fill the lists - ProjectListControl will handle showing tasks under projects
		self._list_with_actions.fill(projects_with_actions, active_only=False, 
			session=self._session, expand_projects=True)
		self._list_no_tasks.fill(projects_no_tasks, active_only=False, 
			session=self._session, expand_projects=False)

	def _on_item_activated_with_tasks(self, evt):
		""" Handle double-click on a project item in projects with actions list. """
		self._on_item_activated(evt, self._list_with_actions)

	def _on_item_activated_no_tasks(self, evt):
		""" Handle double-click on a project item in projects without tasks list. """
		self._on_item_activated(evt, self._list_no_tasks)

	def _on_item_activated(self, evt, list_ctrl):
		""" Handle double-click on a project item. """
		item_idx = evt.GetIndex()
		
		if item_idx >= 0:
			task_uuid = list_ctrl.get_item_uuid(item_idx)
			if task_uuid:
				# Import here to avoid circular dependency
				from wxgtd.gui.task_controller import TaskController
				TaskController.open_task(self, task_uuid)

