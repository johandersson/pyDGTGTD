#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.model.enums module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
from wxgtd.model import enums


class TestEnums:
    """Tests for enum constants and dictionaries."""
    
    def test_statuses_dict_contains_values(self):
        """Test STATUSES dictionary contains expected values."""
        assert 0 in enums.STATUSES
        assert isinstance(enums.STATUSES[0], str)
        assert len(enums.STATUSES) > 0
    
    def test_types_dict_contains_task(self):
        """Test TYPES dictionary contains task type."""
        assert enums.TYPE_TASK in enums.TYPES
        assert isinstance(enums.TYPES[enums.TYPE_TASK], str)
    
    def test_types_dict_contains_project(self):
        """Test TYPES dictionary contains project type."""
        assert enums.TYPE_PROJECT in enums.TYPES
        assert isinstance(enums.TYPES[enums.TYPE_PROJECT], str)
    
    def test_types_dict_contains_checklist(self):
        """Test TYPES dictionary contains checklist type."""
        assert enums.TYPE_CHECKLIST in enums.TYPES
        assert isinstance(enums.TYPES[enums.TYPE_CHECKLIST], str)
    
    def test_type_constants_are_integers(self):
        """Test that type constants are integers."""
        assert isinstance(enums.TYPE_TASK, int)
        assert isinstance(enums.TYPE_PROJECT, int)
        assert isinstance(enums.TYPE_CHECKLIST, int)
        assert isinstance(enums.TYPE_CHECKLIST_ITEM, int)
    
    def test_hide_patterns_list_not_empty(self):
        """Test HIDE_PATTERNS_LIST is not empty."""
        assert len(enums.HIDE_PATTERNS_LIST) > 0
        # Each item should be a tuple of (pattern, description)
        for item in enums.HIDE_PATTERNS_LIST:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], str)
    
    def test_hide_patterns_dict(self):
        """Test HIDE_PATTERNS dictionary."""
        assert len(enums.HIDE_PATTERNS) > 0
        assert "task is due" in enums.HIDE_PATTERNS
        assert "given date" in enums.HIDE_PATTERNS
    
    def test_remind_patterns_list_not_empty(self):
        """Test REMIND_PATTERNS_LIST is not empty."""
        assert len(enums.REMIND_PATTERNS_LIST) > 0
        for item in enums.REMIND_PATTERNS_LIST:
            assert isinstance(item, tuple)
            assert len(item) == 2
    
    def test_remind_patterns_dict(self):
        """Test REMIND_PATTERNS dictionary."""
        assert len(enums.REMIND_PATTERNS) > 0
        assert "due" in enums.REMIND_PATTERNS
        assert "1 day" in enums.REMIND_PATTERNS
    
    def test_snooze_patterns(self):
        """Test SNOOZE_PATTERNS."""
        assert len(enums.SNOOZE_PATTERNS) > 0
        # Snooze patterns should not include 'due'
        patterns = [p[0] for p in enums.SNOOZE_PATTERNS]
        assert "due" not in patterns
    
    def test_priorities_dict(self):
        """Test PRIORITIES dictionary."""
        assert len(enums.PRIORITIES) > 0
        assert 0 in enums.PRIORITIES  # Low
        assert 1 in enums.PRIORITIES  # Med
        assert 2 in enums.PRIORITIES  # High
        assert 3 in enums.PRIORITIES  # TOP
        assert -1 in enums.PRIORITIES  # None
    
    def test_repeat_pattern_list_not_empty(self):
        """Test REPEAT_PATTERN_LIST is not empty."""
        assert len(enums.REPEAT_PATTERN_LIST) > 0
        for item in enums.REPEAT_PATTERN_LIST:
            assert isinstance(item, tuple)
            assert len(item) == 2
    
    def test_repeat_pattern_dict(self):
        """Test REPEAT_PATTERN dictionary."""
        assert len(enums.REPEAT_PATTERN) > 0
        assert "Norepeat" in enums.REPEAT_PATTERN
        assert "Daily" in enums.REPEAT_PATTERN
        assert "Weekly" in enums.REPEAT_PATTERN
        assert "Monthly" in enums.REPEAT_PATTERN
        assert "Yearly" in enums.REPEAT_PATTERN
    
    def test_goal_time_term_dict(self):
        """Test GOAL_TIME_TERM dictionary."""
        assert len(enums.GOAL_TIME_TERM) > 0
        assert 0 in enums.GOAL_TIME_TERM  # Lifelong
        assert 1 in enums.GOAL_TIME_TERM  # Long Term
        assert 2 in enums.GOAL_TIME_TERM  # Short Term
