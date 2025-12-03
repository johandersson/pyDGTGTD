#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.logic.quicktask module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
from unittest.mock import Mock, patch

from wxgtd.logic import quicktask
from wxgtd.model import objects as OBJ


class TestCreateQuicktask:
    """Tests for create_quicktask function."""
    
    @patch('wxgtd.model.objects.Session')
    def test_create_quicktask_with_title(self, mock_session):
        """Test creating a quick task with a title."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        mock_session.return_value = session
        
        result = quicktask.create_quicktask("Buy milk")
        
        assert result is not None
        assert isinstance(result, str)
        # Check that the task was created
        task = session.query(OBJ.Task).filter_by(uuid=result).first()
        assert task is not None
        assert task.title == "Buy milk"
        assert task.priority == -1
    
    @patch('wxgtd.model.objects.Session')
    def test_create_quicktask_empty_title(self, mock_session):
        """Test creating a quick task with empty title."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        mock_session.return_value = session
        
        result = quicktask.create_quicktask("")
        
        assert result is not None
        assert isinstance(result, str)
        # Check that the task was created
        task = session.query(OBJ.Task).filter_by(uuid=result).first()
        assert task is not None
        assert task.title == ""
        assert task.priority == -1
    
    @patch('wxgtd.model.objects.Session')
    def test_create_quicktask_special_characters(self, mock_session):
        """Test creating a quick task with special characters."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        mock_session.return_value = session
        
        title = "Task with @context #tag due:tomorrow"
        result = quicktask.create_quicktask(title)
        
        assert result is not None
        assert isinstance(result, str)
        # Check that the task was created
        task = session.query(OBJ.Task).filter_by(uuid=result).first()
        assert task is not None
        assert task.title == title

