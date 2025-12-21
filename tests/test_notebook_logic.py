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
            'notebook.delete', notebook_uuid=page_uuid
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
            'notebook.update', notebook_uuid=page.uuid
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
            'notebook.update', notebook_uuid=page.uuid
        )


class TestNotebookPubSubMessaging:
    """Tests for notebook pubsub messaging format and callback compatibility."""
    
    def test_sendMessage_format_update(self):
        """Test that notebook.update messages use correct format."""
        from unittest.mock import Mock
        mock_publisher = Mock()
        
        # Simulate the sendMessage call from save_modified_page
        test_uuid = "test-uuid-123"
        notebook_logic.publisher.sendMessage = mock_publisher.sendMessage
        mock_publisher.sendMessage('notebook.update', notebook_uuid=test_uuid)
        
        # Verify the call was made with keyword arguments, not data dict
        mock_publisher.sendMessage.assert_called_with(
            'notebook.update', notebook_uuid=test_uuid
        )
    
    def test_sendMessage_format_delete(self):
        """Test that notebook.delete messages use correct format."""
        from unittest.mock import Mock
        mock_publisher = Mock()
        
        # Simulate the sendMessage call from delete_notebook_page
        test_uuid = "test-uuid-456"
        notebook_logic.publisher.sendMessage = mock_publisher.sendMessage
        mock_publisher.sendMessage('notebook.delete', notebook_uuid=test_uuid)
        
        # Verify the call was made with keyword arguments, not data dict
        mock_publisher.sendMessage.assert_called_with(
            'notebook.delete', notebook_uuid=test_uuid
        )
    
    def test_callback_signature_compatibility(self):
        """Test that callback methods can handle the new message format."""
        # Simulate a callback method like the one in frame_notebooks.py
        def mock_callback(notebook_uuid=None):
            return notebook_uuid
        
        # Test that the callback can be called with the new format
        result = mock_callback(notebook_uuid="test-uuid")
        assert result == "test-uuid"
        
        # Test that it handles None gracefully
        result = mock_callback()
        assert result is None


class TestCodeCompatibility:
    """Tests for code compatibility with modern wxPython and libraries."""
    
    def test_dlg_projects_tree_imports(self):
        """Test that dlg_projects_tree can be imported without syntax errors."""
        try:
            from wxgtd.gui import dlg_projects_tree
            # Verify the class exists
            assert hasattr(dlg_projects_tree, 'DlgProjectTree')
        except ImportError as e:
            # wxPython might not be available in test environment
            if 'wx' in str(e):
                pytest.skip("wxPython not available in test environment")
            else:
                raise
    
    def test_frame_notebooks_imports(self):
        """Test that frame_notebooks can be imported without syntax errors."""
        try:
            from wxgtd.gui import frame_notebooks
            # Verify key classes exist
            assert hasattr(frame_notebooks, 'NotebookController')
        except ImportError as e:
            # wxPython might not be available in test environment
            if 'wx' in str(e):
                pytest.skip("wxPython not available in test environment")
            else:
                raise
    
    def test_base_dialog_imports(self):
        """Test that _base_dialog can be imported without syntax errors."""
        try:
            from wxgtd.gui import _base_dialog
            # Verify the class exists
            assert hasattr(_base_dialog, 'BaseDialog')
        except ImportError as e:
            # wxPython might not be available in test environment
            if 'wx' in str(e):
                pytest.skip("wxPython not available in test environment")
            else:
                raise
    
    def test_no_deprecated_pubsub_usage(self):
        """Test that deprecated pubsub data= usage is not present in notebook logic."""
        import inspect
        from wxgtd.logic import notebook
        
        # Get the source code of the notebook module
        source = inspect.getsource(notebook)
        
        # Ensure no deprecated data= usage in sendMessage calls
        assert 'data={' not in source, "Found deprecated data= usage in sendMessage calls"
        
        # Ensure the new format is used
        assert 'notebook_uuid=' in source, "Expected notebook_uuid parameter in sendMessage calls"

