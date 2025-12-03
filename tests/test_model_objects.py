#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.model.objects module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wxgtd.model import objects as OBJ
from wxgtd.model import enums


class TestGenerateUuid:
    """Tests for generate_uuid function."""
    
    def test_generate_uuid_returns_string(self):
        """Test that generate_uuid returns a string."""
        result = OBJ.generate_uuid()
        assert isinstance(result, str)
    
    def test_generate_uuid_is_unique(self):
        """Test that generate_uuid generates unique values."""
        uuid1 = OBJ.generate_uuid()
        uuid2 = OBJ.generate_uuid()
        assert uuid1 != uuid2
    
    def test_generate_uuid_format(self):
        """Test that generated UUID has correct format."""
        result = OBJ.generate_uuid()
        # UUID4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
        assert len(result) == 36
        assert result.count('-') == 4


class TestBaseModelMixin:
    """Tests for BaseModelMixin methods."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_save_object(self):
        """Test saving an object."""
        task = OBJ.Task(title="Test Task")
        self.session.add(task)
        self.session.commit()
        
        # Verify it's in the database
        saved_task = self.session.query(OBJ.Task).filter_by(
            title="Test Task"
        ).first()
        assert saved_task is not None
        assert saved_task.title == "Test Task"
    
    def test_load_from_dict(self):
        """Test loading attributes from dictionary."""
        task = OBJ.Task(title="Original")
        data = {'title': 'Updated', 'priority': 2}
        
        task.load_from_dict(data)
        
        assert task.title == 'Updated'
        assert task.priority == 2
    
    def test_clone_object(self):
        """Test cloning an object."""
        task = OBJ.Task(
            title="Original Task",
            priority=1,
            note="Test note"
        )
        self.session.add(task)
        self.session.commit()
        
        cloned = task.clone()
        
        assert cloned.title == task.title
        assert cloned.priority == task.priority
        assert cloned.note == task.note
        assert cloned.uuid is None  # UUID should be cleared
    
    def test_clone_without_cleanup(self):
        """Test cloning without cleanup keeps UUID."""
        task = OBJ.Task(title="Test")
        self.session.add(task)
        self.session.commit()
        original_uuid = task.uuid
        
        cloned = task.clone(cleanup=False)
        
        assert cloned.uuid == original_uuid
    
    def test_update_modify_time(self):
        """Test updating modification time."""
        import time
        task = OBJ.Task(title="Test")
        self.session.add(task)
        self.session.commit()
        
        original_modified = task.modified
        time.sleep(0.01)  # Small delay to ensure different timestamp
        
        task.update_modify_time()
        
        assert task.modified >= original_modified
    
    def test_get_method(self):
        """Test get class method."""
        task = OBJ.Task(title="Unique Task")
        self.session.add(task)
        self.session.commit()
        
        result = OBJ.Task.get(self.session, title="Unique Task")
        
        assert result is not None
        assert result.title == "Unique Task"
    
    def test_all_method(self):
        """Test all class method."""
        task1 = OBJ.Task(title="Task 1")
        task2 = OBJ.Task(title="Task 2")
        self.session.add_all([task1, task2])
        self.session.commit()
        
        results = OBJ.Task.all(session=self.session).all()
        
        assert len(results) >= 2
    
    def test_all_excludes_deleted(self):
        """Test all method excludes deleted items."""
        task1 = OBJ.Task(title="Active")
        task2 = OBJ.Task(title="Deleted", deleted=datetime.datetime.now())
        self.session.add_all([task1, task2])
        self.session.commit()
        
        results = OBJ.Task.all(session=self.session).all()
        
        titles = [t.title for t in results]
        assert "Active" in titles
        assert "Deleted" not in titles
    
    def test_get_deleted_method(self):
        """Test get_deleted class method."""
        task1 = OBJ.Task(title="Active")
        task2 = OBJ.Task(title="Deleted", deleted=datetime.datetime.now())
        self.session.add_all([task1, task2])
        self.session.commit()
        
        results = OBJ.Task.get_deleted(session=self.session).all()
        
        assert len(results) == 1
        assert results[0].title == "Deleted"


class TestTask:
    """Tests for Task model."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_create_task(self):
        """Test creating a basic task."""
        task = OBJ.Task(title="Test Task", priority=1)
        self.session.add(task)
        self.session.commit()
        
        assert task.uuid is not None
        assert task.created is not None
        assert task.modified is not None
        assert task.type == enums.TYPE_TASK
    
    def test_task_completed_property_get(self):
        """Test getting task_completed property."""
        task = OBJ.Task(title="Test")
        self.session.add(task)
        self.session.commit()
        
        assert task.task_completed is False
        
        task.completed = datetime.datetime.now()
        assert task.task_completed is True
    
    def test_task_completed_property_set(self):
        """Test setting task_completed property."""
        task = OBJ.Task(title="Test")
        self.session.add(task)
        self.session.commit()
        
        task.task_completed = True
        assert task.completed is not None
        
        task.task_completed = False
        assert task.completed is None
    
    def test_status_name_property(self):
        """Test status_name property."""
        task = OBJ.Task(title="Test", status=1)
        assert task.status_name in enums.STATUSES.values()
    
    def test_overdue_property_not_completed(self):
        """Test overdue property for task not completed."""
        past_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        task = OBJ.Task(
            title="Overdue Task",
            due_date=past_date,
            completed=None
        )
        self.session.add(task)
        self.session.commit()
        
        assert task.overdue is True
    
    def test_overdue_property_completed(self):
        """Test overdue property for completed task."""
        past_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        task = OBJ.Task(
            title="Completed Task",
            due_date=past_date,
            completed=datetime.datetime.now()
        )
        self.session.add(task)
        self.session.commit()
        
        assert task.overdue is False
    
    def test_overdue_property_future_due(self):
        """Test overdue property for future due date."""
        future_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        task = OBJ.Task(
            title="Future Task",
            due_date=future_date,
            completed=None
        )
        self.session.add(task)
        self.session.commit()
        
        assert task.overdue is False
    
    def test_all_projects_method(self):
        """Test all_projects class method."""
        project1 = OBJ.Task(title="Project 1", type=enums.TYPE_PROJECT)
        project2 = OBJ.Task(title="Project 2", type=enums.TYPE_PROJECT)
        task = OBJ.Task(title="Task", type=enums.TYPE_TASK)
        self.session.add_all([project1, project2, task])
        self.session.commit()
        
        # Temporarily bind session
        OBJ.Session.configure(bind=self.session.bind)
        
        results = OBJ.Task.all_projects().all()
        
        assert len(results) == 2
        assert all(t.type == enums.TYPE_PROJECT for t in results)
    
    def test_all_checklists_method(self):
        """Test all_checklists class method."""
        checklist1 = OBJ.Task(title="Checklist 1", type=enums.TYPE_CHECKLIST)
        checklist2 = OBJ.Task(title="Checklist 2", type=enums.TYPE_CHECKLIST)
        task = OBJ.Task(title="Task", type=enums.TYPE_TASK)
        self.session.add_all([checklist1, checklist2, task])
        self.session.commit()
        
        # Temporarily bind session
        OBJ.Session.configure(bind=self.session.bind)
        
        results = OBJ.Task.all_checklists().all()
        
        assert len(results) == 2
        assert all(t.type == enums.TYPE_CHECKLIST for t in results)
    
    def test_find_max_importance(self):
        """Test find_max_importance class method."""
        parent = OBJ.Task(title="Parent", type=enums.TYPE_CHECKLIST)
        self.session.add(parent)
        self.session.commit()
        
        child1 = OBJ.Task(
            title="Child 1",
            parent_uuid=parent.uuid,
            importance=1
        )
        child2 = OBJ.Task(
            title="Child 2",
            parent_uuid=parent.uuid,
            importance=3
        )
        child3 = OBJ.Task(
            title="Child 3",
            parent_uuid=parent.uuid,
            importance=2
        )
        self.session.add_all([child1, child2, child3])
        self.session.commit()
        
        max_importance = OBJ.Task.find_max_importance(
            parent.uuid,
            self.session
        )
        
        assert max_importance == 3


class TestGoal:
    """Tests for Goal model."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_create_goal(self):
        """Test creating a goal."""
        goal = OBJ.Goal(title="Learn Python")
        self.session.add(goal)
        self.session.commit()
        
        assert goal.uuid is not None
        assert goal.title == "Learn Python"
    
    def test_goal_with_time_period(self):
        """Test creating a goal with time_period."""
        goal = OBJ.Goal(title="Short term goal", time_period=2)
        self.session.add(goal)
        self.session.commit()
        
        assert goal.time_period == 2


class TestFolder:
    """Tests for Folder model."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_create_folder(self):
        """Test creating a folder."""
        folder = OBJ.Folder(title="Work")
        self.session.add(folder)
        self.session.commit()
        
        assert folder.uuid is not None
        assert folder.title == "Work"


class TestContext:
    """Tests for Context model."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_create_context(self):
        """Test creating a context."""
        context = OBJ.Context(title="Office")
        self.session.add(context)
        self.session.commit()
        
        assert context.uuid is not None
        assert context.title == "Office"


class TestNotebookPage:
    """Tests for NotebookPage model."""
    
    def setup_method(self):
        """Set up test database."""
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def teardown_method(self):
        """Clean up test database."""
        self.session.close()
    
    def test_create_notebook_page(self):
        """Test creating a notebook page."""
        page = OBJ.NotebookPage(title="Notes", note="Some content")
        self.session.add(page)
        self.session.commit()
        
        assert page.uuid is not None
        assert page.title == "Notes"
        assert page.note == "Some content"

