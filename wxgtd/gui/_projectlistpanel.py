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
import wx.lib.agw.ultimatelistctrl as ULC

from wxgtd.model import objects as OBJ
from wxgtd.model import enums
from wxgtd.wxtools import iconprovider

_ = gettext.gettext
_LOG = logging.getLogger(__name__)


class ProjectListPanel(wx.Panel):
	""" Panel that displays projects in two categories:
	- Projects with actions (have tasks)
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

		self._list_with_actions = self._create_list_ctrl()
		main_sizer.Add(self._list_with_actions, 1, 
			wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		# Projects with no tasks section
		label_no_tasks = wx.StaticText(self, -1, 
			_("Projects with No Tasks"))
		font = label_no_tasks.GetFont()
		font = font.Bold()
		label_no_tasks.SetFont(font)
		main_sizer.Add(label_no_tasks, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

		self._list_no_tasks = self._create_list_ctrl()
		main_sizer.Add(self._list_no_tasks, 1, 
			wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		self.SetSizer(main_sizer)

		# Bind double-click events
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)

	def _create_list_ctrl(self):
		""" Create a list control for displaying projects. """
		list_ctrl = ULC.UltimateListCtrl(self, -1,
			agwStyle=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_HRULES |
			ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)

		# Set font
		font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		list_ctrl.SetFont(font)

		# Setup columns
		list_ctrl.InsertColumn(0, _("Project"), width=400)
		list_ctrl.InsertColumn(1, _("Tasks"), width=80)
		list_ctrl.InsertColumn(2, _("Starred"), width=80)
		list_ctrl.InsertColumn(3, _("Priority"), width=80)

		# Setup icon list
		self._icons = iconprovider.IconProvider(16)
		self._icons.load_icons(['task_starred', 'project_small'])
		list_ctrl.SetImageList(self._icons.image_list, wx.IMAGE_LIST_SMALL)

		return list_ctrl

	def refresh(self, session=None):
		""" Refresh the project list from the database. """
		self._session = session or OBJ.Session()
		
		# Clear existing items
		self._list_with_actions.DeleteAllItems()
		self._list_no_tasks.DeleteAllItems()

		# Get all projects
		projects = OBJ.Task.all_projects().all()

		projects_with_actions = []
		projects_no_tasks = []

		# Categorize projects
		for project in projects:
			if project.completed:
				continue  # Skip completed projects
			
			# Count children (tasks) - using cached property
			child_count = project.child_count
			
			if child_count > 0:
				projects_with_actions.append((project, child_count))
			else:
				projects_no_tasks.append((project, child_count))

		# Fill the lists
		self._fill_list(self._list_with_actions, projects_with_actions)
		self._fill_list(self._list_no_tasks, projects_no_tasks)

	def _fill_list(self, list_ctrl, projects_data):
		""" Fill a list control with project data. 
		
		Args:
			list_ctrl: The UltimateListCtrl to fill
			projects_data: List of tuples (project, child_count)
		"""
		icon_starred = self._icons.get_image_index('task_starred')
		icon_project = self._icons.get_image_index('project_small')

		for idx, (project, child_count) in enumerate(projects_data):
			# Add project title with icon
			list_idx = list_ctrl.InsertImageStringItem(idx, project.title, icon_project)
			
			# Store project UUID as item data
			list_ctrl.SetItemData(list_idx, id(project))
			list_ctrl.SetItemPyData(list_idx, project.uuid)

			# Task count
			list_ctrl.SetStringItem(list_idx, 1, str(child_count))

			# Starred
			if project.starred:
				list_ctrl.SetStringItem(list_idx, 2, "★")

			# Priority
			if project.priority is not None and project.priority != 0:
				priority_text = str(project.priority)
				if project.priority > 0:
					priority_text = "+" + priority_text
				list_ctrl.SetStringItem(list_idx, 3, priority_text)

	def _on_item_activated(self, evt):
		""" Handle double-click on a project item. """
		list_ctrl = evt.GetEventObject()
		item_idx = evt.GetIndex()
		
		if item_idx >= 0:
			project_uuid = list_ctrl.GetItemPyData(item_idx)
			if project_uuid:
				# Import here to avoid circular dependency
				from wxgtd.gui.task_controller import TaskController
				TaskController.open_task(self, project_uuid)
