#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.logic.dicts module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
from unittest.mock import Mock, patch

from wxgtd.logic import dicts as dicts_logic
from wxgtd.model import objects as OBJ


class TestFindOrCreateGoal:
    """Tests for find_or_create_goal function."""
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_find_existing_goal(self, mock_publisher):
        """Test finding an existing goal."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        existing_goal = OBJ.Goal(title="Existing Goal")
        session.add(existing_goal)
        session.commit()
        
        result = dicts_logic.find_or_create_goal("Existing Goal", session)
        
        assert result is not None
        assert result.uuid == existing_goal.uuid
        assert result.title == "Existing Goal"
        mock_publisher.sendMessage.assert_not_called()
    
    @patch('wxgtd.logic.dicts.publisher')
    def test_create_new_goal(self, mock_publisher):
        """Test creating a new goal."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        result = dicts_logic.find_or_create_goal("New Goal", session)
        
        assert result is not None
        assert result.title == "New Goal"
        # Verify it's in the database
        saved_goal = session.query(OBJ.Goal).filter_by(title="New Goal").first()
        assert saved_goal is not None
        mock_publisher.sendMessage.assert_called_with('goal.update')


class TestFindOrCreateFolder:
    """Tests for find_or_create_folder function."""
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_find_existing_folder(self, mock_publisher):
        """Test finding an existing folder."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        existing_folder = OBJ.Folder(title="Work")
        session.add(existing_folder)
        session.commit()
        
        result = dicts_logic.find_or_create_folder("Work", session)
        
        assert result is not None
        assert result.uuid == existing_folder.uuid
        assert result.title == "Work"
        mock_publisher.sendMessage.assert_not_called()
    
    @patch('wxgtd.logic.dicts.publisher')
    def test_create_new_folder(self, mock_publisher):
        """Test creating a new folder."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        result = dicts_logic.find_or_create_folder("Personal", session)
        
        assert result is not None
        assert result.title == "Personal"
        # Verify it's in the database
        saved_folder = session.query(OBJ.Folder).filter_by(
            title="Personal"
        ).first()
        assert saved_folder is not None
        mock_publisher.sendMessage.assert_called_with('folder.update')


class TestFindOrCreateContext:
    """Tests for find_or_create_context function."""
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_find_existing_context(self, mock_publisher):
        """Test finding an existing context."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        existing_context = OBJ.Context(title="Office")
        session.add(existing_context)
        session.commit()
        
        result = dicts_logic.find_or_create_context("Office", session)
        
        assert result is not None
        assert result.uuid == existing_context.uuid
        assert result.title == "Office"
        mock_publisher.sendMessage.assert_not_called()
    
    @patch('wxgtd.logic.dicts.publisher')
    def test_create_new_context(self, mock_publisher):
        """Test creating a new context."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        result = dicts_logic.find_or_create_context("Home", session)
        
        assert result is not None
        assert result.title == "Home"
        # Verify it's in the database
        saved_context = session.query(OBJ.Context).filter_by(
            title="Home"
        ).first()
        assert saved_context is not None
        mock_publisher.sendMessage.assert_called_with('context.update')


class TestUndeleteDictItem:
    """Tests for undelete_dict_item function."""
    
    @patch('wxgtd.logic.dicts.publisher')
    def test_undelete_deleted_item(self, mock_publisher):
        """Test undeleting a deleted item."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        goal = OBJ.Goal(title="Test Goal")
        goal.deleted = datetime.datetime.now()
        session.add(goal)
        session.commit()
        
        result = dicts_logic.undelete_dict_item(goal, session)
        
        assert result is True
        assert goal.deleted is None
        assert goal.modified is not None
        mock_publisher.sendMessage.assert_called_with('dictitem.update')
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_undelete_non_deleted_item(self, mock_publisher):
        """Test undeleting a non-deleted item."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        goal = OBJ.Goal(title="Test Goal")
        session.add(goal)
        session.commit()
        
        result = dicts_logic.undelete_dict_item(goal, session)
        
        assert result is False
        mock_publisher.sendMessage.assert_not_called()
