#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Pytest configuration and fixtures for wxGTD tests.

Copyright (c) Karol Będkowski, 2013-2014
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
from unittest.mock import Mock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wxgtd.model import objects as OBJ


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine('sqlite:///:memory:')
    OBJ.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def mock_publisher():
    """Mock the publisher for testing without GUI dependencies."""
    with pytest.mock.patch('wxgtd.wxtools.wxpub.publisher') as mock_pub:
        yield mock_pub


@pytest.fixture
def sample_task(db_session):
    """Create a sample task for testing."""
    task = OBJ.Task(
        title="Test Task",
        priority=1,
        type=OBJ.enums.TYPE_TASK,
        created=datetime.datetime(2025, 1, 1, 12, 0, 0),
        modified=datetime.datetime(2025, 1, 1, 12, 0, 0)
    )
    db_session.add(task)
    db_session.commit()
    return task


@pytest.fixture
def sample_project(db_session):
    """Create a sample project for testing."""
    project = OBJ.Task(
        title="Test Project",
        priority=1,
        type=OBJ.enums.TYPE_PROJECT,
        created=datetime.datetime(2025, 1, 1, 12, 0, 0),
        modified=datetime.datetime(2025, 1, 1, 12, 0, 0)
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_checklist(db_session):
    """Create a sample checklist for testing."""
    checklist = OBJ.Task(
        title="Test Checklist",
        priority=1,
        type=OBJ.enums.TYPE_CHECKLIST,
        created=datetime.datetime(2025, 1, 1, 12, 0, 0),
        modified=datetime.datetime(2025, 1, 1, 12, 0, 0)
    )
    db_session.add(checklist)
    db_session.commit()
    return checklist

