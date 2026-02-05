#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for Project List Panel.

Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wxgtd.model import objects as OBJ
from wxgtd.model import enums


class TestProjectCategorization:
	"""Tests for project categorization logic."""

	def setup_method(self):
		"""Set up test database."""
		engine = create_engine('sqlite:///:memory:')
		OBJ.Base.metadata.create_all(engine)
		Session = sessionmaker(bind=engine)
		self.session = Session()
		# Configure global Session for Task.all_projects()
		OBJ.Session.configure(bind=engine)

	def teardown_method(self):
		"""Clean up test database."""
		self.session.close()

	def test_empty_project_has_no_tasks(self):
		"""Test that empty project has child_count of 0."""
		project = OBJ.Task(
			title="Empty Project",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project)
		self.session.commit()

		assert project.child_count == 0

	def test_project_with_one_task(self):
		"""Test that project with one task has child_count of 1."""
		project = OBJ.Task(
			title="Project with Task",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project)
		self.session.commit()

		task = OBJ.Task(
			title="Task",
			type=enums.TYPE_TASK,
			parent_uuid=project.uuid,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(task)
		self.session.commit()

		# Need to clear cache
		if hasattr(project, '_child_count_cache'):
			delattr(project, '_child_count_cache')
		
		assert project.child_count == 1

	def test_project_with_multiple_tasks(self):
		"""Test that project with multiple tasks has correct child_count."""
		project = OBJ.Task(
			title="Project with Multiple Tasks",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project)
		self.session.commit()

		for i in range(5):
			task = OBJ.Task(
				title=f"Task {i}",
				type=enums.TYPE_TASK,
				parent_uuid=project.uuid,
				created=datetime.datetime.now(),
				modified=datetime.datetime.now()
			)
			self.session.add(task)
		self.session.commit()

		# Need to clear cache
		if hasattr(project, '_child_count_cache'):
			delattr(project, '_child_count_cache')
		
		assert project.child_count == 5

	def test_project_with_deleted_task_not_counted(self):
		"""Test that deleted tasks are not counted in child_count."""
		project = OBJ.Task(
			title="Project",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project)
		self.session.commit()

		task1 = OBJ.Task(
			title="Active Task",
			type=enums.TYPE_TASK,
			parent_uuid=project.uuid,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		task2 = OBJ.Task(
			title="Deleted Task",
			type=enums.TYPE_TASK,
			parent_uuid=project.uuid,
			deleted=datetime.datetime.now(),
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add_all([task1, task2])
		self.session.commit()

		# Need to clear cache
		if hasattr(project, '_child_count_cache'):
			delattr(project, '_child_count_cache')
		
		# Should count only active task
		assert project.child_count == 1

	def test_all_projects_query(self):
		"""Test that all_projects() returns only projects."""
		project1 = OBJ.Task(
			title="Project 1",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		project2 = OBJ.Task(
			title="Project 2",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		task = OBJ.Task(
			title="Regular Task",
			type=enums.TYPE_TASK,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		checklist = OBJ.Task(
			title="Checklist",
			type=enums.TYPE_CHECKLIST,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add_all([project1, project2, task, checklist])
		self.session.commit()

		projects = OBJ.Task.all_projects().all()
		
		assert len(projects) == 2
		assert all(p.type == enums.TYPE_PROJECT for p in projects)

	def test_completed_projects_in_query(self):
		"""Test that completed projects are included in all_projects()."""
		project1 = OBJ.Task(
			title="Active Project",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		project2 = OBJ.Task(
			title="Completed Project",
			type=enums.TYPE_PROJECT,
			completed=datetime.datetime.now(),
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add_all([project1, project2])
		self.session.commit()

		projects = OBJ.Task.all_projects().all()
		
		# Should get both (filtering for active happens in the panel)
		assert len(projects) == 2

	def test_deleted_projects_excluded(self):
		"""Test that deleted projects are excluded from all_projects()."""
		project1 = OBJ.Task(
			title="Active Project",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		project2 = OBJ.Task(
			title="Deleted Project",
			type=enums.TYPE_PROJECT,
			deleted=datetime.datetime.now(),
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add_all([project1, project2])
		self.session.commit()

		projects = OBJ.Task.all_projects().all()
		
		assert len(projects) == 1
		assert projects[0].title == "Active Project"

	def test_categorize_projects_with_and_without_tasks(self):
		"""Test categorizing projects into with/without tasks."""
		# Project with tasks
		project_with_tasks = OBJ.Task(
			title="Project with Tasks",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project_with_tasks)
		self.session.commit()

		task = OBJ.Task(
			title="Task",
			type=enums.TYPE_TASK,
			parent_uuid=project_with_tasks.uuid,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(task)

		# Project without tasks
		project_no_tasks = OBJ.Task(
			title="Empty Project",
			type=enums.TYPE_PROJECT,
			created=datetime.datetime.now(),
			modified=datetime.datetime.now()
		)
		self.session.add(project_no_tasks)
		self.session.commit()

		projects = OBJ.Task.all_projects().all()
		
		projects_with_actions = []
		projects_no_actions = []
		
		for project in projects:
			if project.completed:
				continue
			
			if hasattr(project, '_child_count_cache'):
				delattr(project, '_child_count_cache')
			
			if project.child_count > 0:
				projects_with_actions.append(project)
			else:
				projects_no_actions.append(project)
		
		assert len(projects_with_actions) == 1
		assert len(projects_no_actions) == 1
		assert projects_with_actions[0].title == "Project with Tasks"
		assert projects_no_actions[0].title == "Empty Project"
