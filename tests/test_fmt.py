#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.lib.fmt module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
import time

from wxgtd.lib import fmt


class TestFormatTimestamp:
    """Tests for format_timestamp function."""
    
    def test_format_none(self):
        """Test formatting None returns empty string."""
        result = fmt.format_timestamp(None)
        assert result == ""
    
    def test_format_empty_string(self):
        """Test formatting empty string returns empty string."""
        result = fmt.format_timestamp("")
        assert result == ""
    
    def test_format_string_passthrough(self):
        """Test formatting string returns the same string."""
        test_str = "2025-01-01"
        result = fmt.format_timestamp(test_str)
        assert result == test_str
    
    def test_format_datetime_with_time(self):
        """Test formatting datetime object with time."""
        dt = datetime.datetime(2025, 1, 15, 14, 30, 45)
        result = fmt.format_timestamp(dt, show_time=True, datetime_in_utc=False)
        
        # Should contain date and time
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_datetime_without_time(self):
        """Test formatting datetime object without time."""
        dt = datetime.datetime(2025, 1, 15, 14, 30, 45)
        result = fmt.format_timestamp(dt, show_time=False, datetime_in_utc=False)
        
        # Should contain only date
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_datetime_utc_conversion(self):
        """Test formatting datetime with UTC to local conversion."""
        dt = datetime.datetime(2025, 1, 15, 12, 0, 0)
        result = fmt.format_timestamp(dt, show_time=True, datetime_in_utc=True)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_numeric_timestamp_with_time(self):
        """Test formatting numeric timestamp with time."""
        timestamp = time.time()
        result = fmt.format_timestamp(timestamp, show_time=True)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_numeric_timestamp_without_time(self):
        """Test formatting numeric timestamp without time."""
        timestamp = time.time()
        result = fmt.format_timestamp(timestamp, show_time=False)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_zero_timestamp(self):
        """Test formatting zero timestamp."""
        result = fmt.format_timestamp(0, show_time=True)
        
        # Zero timestamp returns empty string or formats as epoch
        assert isinstance(result, str)

