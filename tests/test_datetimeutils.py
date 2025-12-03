#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.lib.datetimeutils module.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
import time

from wxgtd.lib import datetimeutils as DTU


class TestDatetimeUtils:
    """Tests for datetime utility functions."""
    
    def test_datetime_utc2local(self):
        """Test UTC to local time conversion."""
        utc_time = datetime.datetime(2025, 1, 1, 12, 0, 0)
        local_time = DTU.datetime_utc2local(utc_time)
        
        # Result should have local timezone
        assert local_time.tzinfo is not None
        assert isinstance(local_time, datetime.datetime)
    
    def test_datetime_local2utc(self):
        """Test local to UTC time conversion."""
        local_time = datetime.datetime(2025, 1, 1, 12, 0, 0)
        utc_time = DTU.datetime_local2utc(local_time)
        
        # Result should be naive datetime (no timezone)
        assert utc_time.tzinfo is None
        assert isinstance(utc_time, datetime.datetime)
    
    def test_datetime2timestamp_with_conversion(self):
        """Test datetime to timestamp conversion with UTC to local."""
        dt = datetime.datetime(2025, 1, 1, 12, 0, 0)
        timestamp = DTU.datetime2timestamp(dt, utc2local=True)
        
        assert isinstance(timestamp, float)
        assert timestamp > 0
    
    def test_datetime2timestamp_without_conversion(self):
        """Test datetime to timestamp conversion without UTC to local."""
        dt = datetime.datetime(2025, 1, 1, 12, 0, 0)
        timestamp = DTU.datetime2timestamp(dt, utc2local=False)
        
        assert isinstance(timestamp, float)
        assert timestamp > 0
    
    def test_timestamp2datetime_with_conversion(self):
        """Test timestamp to datetime conversion with local to UTC."""
        timestamp = time.time()
        dt = DTU.timestamp2datetime(timestamp, local2utc=True)
        
        assert isinstance(dt, datetime.datetime)
        # Should be naive datetime
        assert dt.tzinfo is None
    
    def test_timestamp2datetime_without_conversion(self):
        """Test timestamp to datetime conversion without local to UTC."""
        timestamp = time.time()
        dt = DTU.timestamp2datetime(timestamp, local2utc=False)
        
        assert isinstance(dt, datetime.datetime)
        assert dt.tzinfo is None
    
    def test_roundtrip_conversion(self):
        """Test roundtrip conversion: datetime -> timestamp -> datetime."""
        original_dt = datetime.datetime(2025, 6, 15, 14, 30, 45)
        timestamp = DTU.datetime2timestamp(original_dt, utc2local=False)
        recovered_dt = DTU.timestamp2datetime(timestamp, local2utc=False)
        
        # Should be close (within a second due to precision)
        assert abs((original_dt - recovered_dt).total_seconds()) < 1

