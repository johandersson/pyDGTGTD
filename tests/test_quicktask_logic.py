#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.logic.quicktask module.

Copyright (c) Karol Będkowski, 2013-2014
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
    def test_create_quicktask_with_title(self, mock_session_class):
        """Test creating a quick task with a title."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        result = quicktask.create_quicktask("Buy milk")
        
        assert result is not None
        assert result.title == "Buy milk"
        assert result.priority == -1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('wxgtd.model.objects.Session')
    def test_create_quicktask_empty_title(self, mock_session_class):
        """Test creating a quick task with empty title."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        result = quicktask.create_quicktask("")
        
        assert result is not None
        assert result.title == ""
        assert result.priority == -1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('wxgtd.model.objects.Session')
    def test_create_quicktask_special_characters(self, mock_session_class):
        """Test creating a quick task with special characters."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        title = "Task with @context #tag due:tomorrow"
        result = quicktask.create_quicktask(title)
        
        assert result is not None
        assert result.title == title
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
