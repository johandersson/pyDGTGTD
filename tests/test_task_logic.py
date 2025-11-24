#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.logic.task module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
from unittest.mock import Mock, patch, MagicMock

from wxgtd.logic import task as task_logic
from wxgtd.model import objects as OBJ
from wxgtd.model import enums


class TestAlarmPatternToTime:
    """Tests for alarm_pattern_to_time function."""
    
    def test_day_pattern(self):
        """Test alarm pattern with days."""
        result = task_logic.alarm_pattern_to_time("1 day")
        assert result == datetime.timedelta(days=1)
        
        result = task_logic.alarm_pattern_to_time("3 days")
        assert result == datetime.timedelta(days=3)
    
    def test_hour_pattern(self):
        """Test alarm pattern with hours."""
        result = task_logic.alarm_pattern_to_time("2 hour")
        assert result == datetime.timedelta(hours=2)
        
        result = task_logic.alarm_pattern_to_time("6 hours")
        assert result == datetime.timedelta(hours=6)
    
    def test_minute_pattern(self):
        """Test alarm pattern with minutes."""
        result = task_logic.alarm_pattern_to_time("15 minute")
        assert result == datetime.timedelta(minutes=15)
        
        result = task_logic.alarm_pattern_to_time("30 minutes")
        assert result == datetime.timedelta(minutes=30)
    
    def test_decimal_hours(self):
        """Test alarm pattern with decimal hours."""
        result = task_logic.alarm_pattern_to_time("1.5 hours")
        assert result == datetime.timedelta(hours=1.5)
    
    def test_invalid_pattern(self):
        """Test invalid alarm pattern returns None."""
        result = task_logic.alarm_pattern_to_time("1 week")
        assert result is None


class TestUpdateTaskAlarm:
    """Tests for update_task_alarm function."""
    
    def test_no_alarm_pattern(self):
        """Test update with no alarm pattern."""
        task = Mock()
        task.alarm_pattern = None
        task.alarm = None
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        
        task_logic.update_task_alarm(task)
        # Should not change alarm
        assert task.alarm is None
    
    def test_due_pattern(self):
        """Test update with 'due' pattern."""
        task = Mock()
        task.alarm_pattern = 'due'
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        
        task_logic.update_task_alarm(task)
        assert task.alarm == task.due_date
    
    def test_offset_pattern(self):
        """Test update with time offset pattern."""
        task = Mock()
        task.alarm_pattern = '1 day'
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        
        task_logic.update_task_alarm(task)
        expected = datetime.datetime(2025, 1, 14, 10, 0, 0)
        assert task.alarm == expected
    
    def test_alarm_equals_due_sets_pattern(self):
        """Test alarm equal to due_date sets pattern to 'due'."""
        task = Mock()
        task.alarm_pattern = None
        task.alarm = datetime.datetime(2025, 1, 15, 10, 0, 0)
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        
        task_logic.update_task_alarm(task)
        assert task.alarm_pattern == 'due'


class TestUpdateTaskHide:
    """Tests for update_task_hide function."""
    
    def test_no_hide_pattern(self):
        """Test update with no hide pattern."""
        task = Mock()
        task.hide_pattern = None
        task.hide_until = None
        
        result = task_logic.update_task_hide(task)
        assert result is True
        assert task.hide_until is None
    
    def test_given_date_pattern(self):
        """Test update with 'given date' pattern."""
        task = Mock()
        task.hide_pattern = 'given date'
        task.hide_until = datetime.datetime(2025, 1, 10, 0, 0, 0)
        
        result = task_logic.update_task_hide(task)
        assert result is True
        # hide_until should not change
        assert task.hide_until == datetime.datetime(2025, 1, 10, 0, 0, 0)
    
    def test_task_is_due_pattern(self):
        """Test update with 'task is due' pattern."""
        task = Mock()
        task.hide_pattern = 'task is due'
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        task.start_date = None
        
        result = task_logic.update_task_hide(task)
        assert result is True
        assert task.hide_until == task.due_date
    
    def test_offset_before_due(self):
        """Test update with offset before due date."""
        task = Mock()
        task.hide_pattern = '1 week before due'
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        task.start_date = None
        
        result = task_logic.update_task_hide(task)
        assert result is True
        expected = datetime.datetime(2025, 1, 8, 10, 0, 0)
        assert task.hide_until == expected
    
    def test_offset_before_start(self):
        """Test update with offset before start date."""
        task = Mock()
        task.hide_pattern = '1 day before start'
        task.start_date = datetime.datetime(2025, 1, 10, 10, 0, 0)
        task.due_date = None
        
        result = task_logic.update_task_hide(task)
        assert result is True
        expected = datetime.datetime(2025, 1, 9, 10, 0, 0)
        assert task.hide_until == expected
    
    def test_invalid_pattern(self):
        """Test update with invalid pattern."""
        task = Mock()
        task.hide_pattern = 'invalid pattern'
        
        result = task_logic.update_task_hide(task)
        assert result is False


class TestRepeatPatterns:
    """Tests for repeat pattern building functions."""
    
    def test_build_repeat_pattern_every_xt(self):
        """Test building 'Every X T' pattern."""
        result = task_logic.build_repeat_pattern_every_xt(1, 'Day')
        assert result == "Every 1 Day"
        
        result = task_logic.build_repeat_pattern_every_xt(3, 'Week')
        assert result == "Every 3 Weeks"
        
        result = task_logic.build_repeat_pattern_every_xt(2, 'Month')
        assert result == "Every 2 Months"
    
    def test_build_repeat_pattern_every_w(self):
        """Test building 'Every weekdays' pattern."""
        result = task_logic.build_repeat_pattern_every_w(
            True, False, True, False, True, False, False
        )
        assert result == "Every Mon, Wed, Fri"
        
        result = task_logic.build_repeat_pattern_every_w(
            False, False, False, False, False, True, True
        )
        assert result == "Every Sat, Sun"
    
    def test_build_repeat_pattern_every_xdm(self):
        """Test building 'The X D every M months' pattern."""
        result = task_logic.build_repeat_pattern_every_xdm(
            'first', 'Mon', 1
        )
        assert result == "The first Mon every 1 month"
        
        result = task_logic.build_repeat_pattern_every_xdm(
            'second', 'Fri', 2
        )
        assert result == "The second Fri every 2 months"


class TestMoveDateRepeat:
    """Tests for _move_date_repeat function."""
    
    def test_no_repeat_pattern(self):
        """Test with no repeat pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, None)
        assert result == date
    
    def test_daily_pattern(self):
        """Test daily repeat pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Daily')
        expected = datetime.datetime(2025, 1, 16, 10, 0, 0)
        assert result == expected
    
    def test_weekly_pattern(self):
        """Test weekly repeat pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Weekly')
        expected = datetime.datetime(2025, 1, 22, 10, 0, 0)
        assert result == expected
    
    def test_monthly_pattern(self):
        """Test monthly repeat pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Monthly')
        expected = datetime.datetime(2025, 2, 15, 10, 0, 0)
        assert result == expected
    
    def test_yearly_pattern(self):
        """Test yearly repeat pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Yearly')
        expected = datetime.datetime(2026, 1, 15, 10, 0, 0)
        assert result == expected
    
    def test_businessday_pattern_weekday(self):
        """Test business day pattern on a weekday."""
        # Wednesday
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Businessday')
        # Should move to Thursday
        expected = datetime.datetime(2025, 1, 16, 10, 0, 0)
        assert result == expected
    
    def test_every_x_days(self):
        """Test 'Every X days' pattern."""
        date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        result = task_logic._move_date_repeat(date, 'Every 3 days')
        expected = datetime.datetime(2025, 1, 18, 10, 0, 0)
        assert result == expected


class TestRepeatTask:
    """Tests for repeat_task function."""
    
    @patch('wxgtd.model.objects.generate_uuid')
    def test_no_repeat_pattern(self, mock_uuid):
        """Test repeat_task with no repeat pattern."""
        mock_uuid.return_value = "test-uuid"
        task = Mock()
        task.repeat_pattern = None
        
        result = task_logic.repeat_task(task)
        assert result is None
    
    @patch('wxgtd.model.objects.generate_uuid')
    def test_norepeat_pattern(self, mock_uuid):
        """Test repeat_task with 'Norepeat' pattern."""
        mock_uuid.return_value = "test-uuid"
        task = Mock()
        task.repeat_pattern = 'Norepeat'
        
        result = task_logic.repeat_task(task)
        assert result is None
    
    @patch('wxgtd.model.objects.generate_uuid')
    def test_daily_repeat(self, mock_uuid):
        """Test repeat_task with daily pattern."""
        mock_uuid.return_value = "new-uuid"
        
        task = Mock()
        task.repeat_pattern = 'Daily'
        task.repeat_from = 0
        task.parent_uuid = None
        task.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        task.start_date = None
        task.alarm = None
        task.alarm_pattern = None
        task.hide_pattern = None  # Add this
        task.hide_until = None  # Add this
        task.completed = datetime.datetime(2025, 1, 15, 12, 0, 0)
        
        # Create a more complete mock for the cloned task
        ntask = Mock()
        ntask.uuid = None
        ntask.repeat_pattern = 'Daily'
        ntask.repeat_from = 0
        ntask.parent_uuid = None
        ntask.due_date = datetime.datetime(2025, 1, 15, 10, 0, 0)
        ntask.start_date = None
        ntask.alarm = None
        ntask.alarm_pattern = None
        ntask.hide_pattern = None
        ntask.hide_until = None
        ntask.completed = datetime.datetime(2025, 1, 15, 12, 0, 0)
        ntask.parent = None
        
        task.clone.return_value = ntask
        
        result = task_logic.repeat_task(task)
        
        assert result is not None
        assert result.uuid == "new-uuid"
        assert result.completed is None
        assert task.repeat_pattern == 'Norepeat'


class TestDeleteTask:
    """Tests for delete_task function."""
    
    @patch('wxgtd.logic.task.publisher')
    def test_delete_task_soft(self, mock_publisher):
        """Test soft delete of task."""
        # Create in-memory session
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        task = OBJ.Task(title="Test Task")
        session.add(task)
        session.commit()
        
        result = task_logic.delete_task(task, session=session, permanently=False)
        
        assert result is True
        assert task.deleted is not None
        mock_publisher.sendMessage.assert_called_with('task.delete', task_uuid=task.uuid)
    
    @patch('wxgtd.logic.task.publisher')
    def test_delete_task_permanently(self, mock_publisher):
        """Test permanent delete of task."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        task = OBJ.Task(title="Test Task")
        session.add(task)
        session.commit()
        task_uuid = task.uuid
        
        result = task_logic.delete_task(task, session=session, permanently=True)
        
        assert result is True
        # Task should be deleted from database
        assert session.query(OBJ.Task).filter_by(uuid=task_uuid).first() is None
        mock_publisher.sendMessage.assert_called_with('task.delete', task_uuid=task_uuid)


class TestCompleteTask:
    """Tests for complete_task function."""
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_complete_regular_task(self, mock_publisher):
        """Test completing a regular task."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        task = OBJ.Task(title="Test Task", type=enums.TYPE_TASK)
        session.add(task)
        session.commit()
        
        result = task_logic.complete_task(task, session=session)
        
        assert result is True
        assert task.task_completed is True
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_complete_checklist_item(self, mock_publisher):
        """Test completing a checklist item."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        parent = OBJ.Task(title="Checklist", type=enums.TYPE_CHECKLIST)
        session.add(parent)
        session.commit()
        
        task = OBJ.Task(
            title="Item 1",
            type=enums.TYPE_CHECKLIST_ITEM,
            parent_uuid=parent.uuid,
            importance=1
        )
        session.add(task)
        session.commit()
        
        result = task_logic.complete_task(task, session=session)
        
        assert result is True
        assert task.task_completed is True


class TestToggleFunctions:
    """Tests for toggle functions."""
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_toggle_task_starred(self, mock_publisher):
        """Test toggling task starred flag."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        task = OBJ.Task(title="Test Task", starred=0)
        session.add(task)
        session.commit()
        
        result = task_logic.toggle_task_starred(task.uuid, session=session)
        
        assert result is True
        assert task.starred == 1


class TestAdjustTaskType:
    """Tests for adjust_task_type function."""
    
    def test_adjust_checklist_item_in_checklist(self):
        """Test checklist item in checklist keeps its type."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        parent = OBJ.Task(title="Checklist", type=enums.TYPE_CHECKLIST)
        session.add(parent)
        session.commit()
        
        task = OBJ.Task(
            title="Item",
            type=enums.TYPE_TASK,
            parent_uuid=parent.uuid
        )
        session.add(task)
        session.commit()
        
        result = task_logic.adjust_task_type(task, session)
        
        assert result is True
        assert task.type == enums.TYPE_CHECKLIST_ITEM
    
    def test_adjust_checklist_item_without_parent(self):
        """Test checklist item without parent becomes regular task."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        task = OBJ.Task(title="Item", type=enums.TYPE_CHECKLIST_ITEM)
        session.add(task)
        session.commit()
        
        result = task_logic.adjust_task_type(task, session)
        
        assert result is True
        assert task.type == enums.TYPE_TASK
