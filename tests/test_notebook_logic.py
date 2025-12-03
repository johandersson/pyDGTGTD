#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for wxgtd.logic.notebook module.

Copyright (c) Karol Będkowski, 2013-2025
Copyright (c) Johan Andersson, 2025
Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
from unittest.mock import Mock, patch

from wxgtd.logic import notebook as notebook_logic
from wxgtd.model import objects as OBJ


class TestDeleteNotebookPage:
    """Tests for delete_notebook_page function."""
    
    @patch('wxgtd.logic.notebook.publisher')
    def test_delete_existing_page(self, mock_publisher):
        """Test deleting an existing notebook page."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        page = OBJ.NotebookPage(title="Test Page", note="Test content")
        session.add(page)
        session.commit()
        page_uuid = page.uuid
        
        result = notebook_logic.delete_notebook_page(page_uuid, session=session)
        
        assert result is True
        # Page should be soft-deleted
        deleted_page = session.query(OBJ.NotebookPage).filter_by(
            uuid=page_uuid
        ).first()
        assert deleted_page.deleted is not None
        mock_publisher.sendMessage.assert_called_with(
            'notebook.delete', data={'notebook_uuid': page_uuid}
        )
    
    @patch('wxgtd.wxtools.wxpub.publisher')
    def test_delete_missing_page(self, mock_publisher):
        """Test deleting a non-existent page."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        result = notebook_logic.delete_notebook_page(
            "non-existent-uuid",
            session=session
        )
        
        assert result is False
        mock_publisher.sendMessage.assert_not_called()


class TestSaveModifiedPage:
    """Tests for save_modified_page function."""
    
    @patch('wxgtd.logic.notebook.publisher')
    def test_save_modified_page(self, mock_publisher):
        """Test saving a modified page."""
        import time
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        page = OBJ.NotebookPage(title="Test Page", note="Test content")
        session.add(page)
        session.commit()
        
        original_modified = page.modified
        time.sleep(0.01)  # Small delay to ensure different timestamp
        
        # Modify the page
        page.title = "Updated Title"
        
        result = notebook_logic.save_modified_page(page, session=session)
        
        assert result is True
        assert page.modified >= original_modified
        mock_publisher.sendMessage.assert_called_with(
            'notebook.update', data={'notebook_uuid': page.uuid}
        )
    
    @patch('wxgtd.logic.notebook.publisher')
    def test_save_new_page(self, mock_publisher):
        """Test saving a new page."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        OBJ.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        page = OBJ.NotebookPage(title="New Page", note="New content")
        
        result = notebook_logic.save_modified_page(page, session=session)
        
        assert result is True
        assert page.modified is not None
        # Verify page is in database
        saved_page = session.query(OBJ.NotebookPage).filter_by(
            uuid=page.uuid
        ).first()
        assert saved_page is not None
        assert saved_page.title == "New Page"
        mock_publisher.sendMessage.assert_called_with(
            'notebook.update', data={'notebook_uuid': page.uuid}
        )

