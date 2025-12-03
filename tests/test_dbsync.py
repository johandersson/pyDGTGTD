#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Tests for Dropbox synchronization module.

Copyright (c) Johan Andersson, 2025
License: GPLv2+
"""

import pytest
import datetime
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open
from io import BytesIO

from wxgtd.model import dbsync
from wxgtd.model import sync as SYNC


class MockDropboxMetadata:
	"""Mock Dropbox file metadata."""
	def __init__(self, size=100):
		self.size = size


class MockDropboxResponse:
	"""Mock Dropbox file download response."""
	def __init__(self, content=b"test content"):
		self.content = content


class TestDropboxAvailability:
	"""Test Dropbox availability check."""
	
	def test_is_available_when_dropbox_installed(self):
		"""Test that is_available returns True when dropbox is installed."""
		# The module should have dropbox imported at this point
		assert dbsync.is_available() is True
	
	@patch('wxgtd.model.dbsync.dropbox', None)
	def test_is_available_when_dropbox_not_installed(self):
		"""Test that is_available returns False when dropbox is not installed."""
		assert dbsync.is_available() is False


class TestCreateSession:
	"""Test Dropbox session creation."""
	
	@patch('wxgtd.model.dbsync.dropbox.Dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_with_access_token(self, mock_appconfig, mock_dropbox_class):
		"""Test session creation with access token."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_access_token'
		mock_appconfig.return_value = mock_config
		
		dbsync._create_session()
		
		mock_config.get.assert_any_call('dropbox', 'access_token')
		mock_dropbox_class.assert_called_once_with('test_access_token')
	
	@patch('wxgtd.model.dbsync.dropbox.Dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_fallback_to_oauth_key(self, mock_appconfig, mock_dropbox_class):
		"""Test session creation falls back to oauth_key if access_token not set."""
		mock_config = MagicMock()
		mock_config.get.side_effect = lambda section, key: {
			('dropbox', 'access_token'): None,
			('dropbox', 'oauth_key'): 'old_oauth_key'
		}.get((section, key))
		mock_appconfig.return_value = mock_config
		
		dbsync._create_session()
		
		mock_dropbox_class.assert_called_once_with('old_oauth_key')
	
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_raises_without_credentials(self, mock_appconfig):
		"""Test session creation raises error without credentials."""
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		with pytest.raises(SYNC.OtherSyncError):
			dbsync._create_session()


class TestDownloadFile:
	"""Test file download from Dropbox."""
	
	def test_download_file_success(self):
		"""Test successful file download."""
		mock_client = MagicMock()
		mock_metadata = MockDropboxMetadata(size=12)
		mock_response = MockDropboxResponse(content=b"test content")
		mock_client.files_download.return_value = (mock_metadata, mock_response)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		assert result is True
		assert fileobj.getvalue() == b"test content"
		mock_client.files_download.assert_called_once_with('/test/path.zip')
	
	def test_download_file_empty_file(self):
		"""Test download returns False for empty file."""
		mock_client = MagicMock()
		mock_metadata = MockDropboxMetadata(size=0)
		mock_response = MockDropboxResponse(content=b"")
		mock_client.files_download.return_value = (mock_metadata, mock_response)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		assert result is False
	
	def test_download_file_not_found(self):
		"""Test download handles file not found error."""
		from dropbox.exceptions import ApiError
		
		mock_client = MagicMock()
		mock_client.files_download.side_effect = ApiError(
			request_id='123',
			error=None,
			user_message_text='File not found',
			user_message_locale='en'
		)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		assert result is False


class TestDeleteFile:
	"""Test file deletion from Dropbox."""
	
	def test_delete_file_success(self):
		"""Test successful file deletion."""
		mock_client = MagicMock()
		
		dbsync._delete_file(mock_client, '/test/path.zip')
		
		mock_client.files_delete_v2.assert_called_once_with('/test/path.zip')
	
	def test_delete_file_handles_error(self):
		"""Test delete handles API errors gracefully."""
		from dropbox.exceptions import ApiError
		
		mock_client = MagicMock()
		mock_client.files_delete_v2.side_effect = ApiError(
			request_id='123',
			error=None,
			user_message_text='File not found',
			user_message_locale='en'
		)
		
		# Should not raise exception
		dbsync._delete_file(mock_client, '/test/path.zip')


class TestCreateSyncLock:
	"""Test sync lock creation."""
	
	@patch('wxgtd.model.dbsync.objects.Session')
	@patch('wxgtd.model.dbsync.exporter.fmt_date')
	def test_create_sync_lock_success(self, mock_fmt_date, mock_session_class):
		"""Test successful sync lock creation."""
		mock_client = MagicMock()
		from dropbox.exceptions import ApiError
		
		# Simulate lock file not existing
		mock_client.files_get_metadata.side_effect = ApiError(
			request_id='123',
			error=None,
			user_message_text='Not found',
			user_message_locale='en'
		)
		
		# Mock database session
		mock_session = MagicMock()
		mock_conf = MagicMock()
		mock_conf.val = 'device_123'
		mock_session.query.return_value.filter_by.return_value.first.return_value = mock_conf
		mock_session_class.return_value = mock_session
		
		mock_fmt_date.return_value = '2025-12-03T10:00:00Z'
		
		result = dbsync.create_sync_lock(mock_client)
		
		assert result is True
		mock_client.files_upload.assert_called_once()
		# Verify the lock file contains device ID and timestamp
		call_args = mock_client.files_upload.call_args
		assert b'device_123' in call_args[0][0]
		assert call_args[0][1] == dbsync.LOCK_PATH
	
	@patch('wxgtd.model.dbsync.objects.Session')
	def test_create_sync_lock_already_locked(self, mock_session_class):
		"""Test sync lock creation when already locked."""
		mock_client = MagicMock()
		mock_metadata = MockDropboxMetadata(size=100)
		mock_client.files_get_metadata.return_value = mock_metadata
		
		result = dbsync.create_sync_lock(mock_client)
		
		assert result is False
		mock_client.files_upload.assert_not_called()


class TestSync:
	"""Test main sync function."""
	
	@patch('wxgtd.model.dbsync.dropbox', None)
	def test_sync_raises_when_dropbox_not_available(self):
		"""Test sync raises error when Dropbox is not available."""
		with pytest.raises(SYNC.OtherSyncError, match="not available"):
			dbsync.sync()
	
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_raises_when_not_configured(self, mock_dropbox_module, mock_appconfig):
		"""Test sync raises error when Dropbox is not configured."""
		mock_config = MagicMock()
		mock_config.get.return_value = None
		mock_appconfig.return_value = mock_config
		
		with pytest.raises(SYNC.OtherSyncError, match="not configured"):
			dbsync.sync()
	
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_raises_when_locked(self, mock_dropbox_module, mock_appconfig,
	                                  mock_create_backup, mock_create_session,
	                                  mock_create_lock):
		"""Test sync raises error when sync file is locked."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = False  # Locked
		
		with pytest.raises(SYNC.SyncLockedError):
			dbsync.sync()
	
	@patch('wxgtd.model.dbsync.download_file')
	@patch('wxgtd.model.dbsync.loader.load_from_file')
	@patch('wxgtd.model.dbsync.exporter.save_to_file')
	@patch('wxgtd.model.dbsync._delete_file')
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('builtins.open', new_callable=mock_open, read_data=b'sync data')
	@patch('os.unlink')
	def test_sync_load_only(self, mock_unlink, mock_file_open, mock_dropbox_module,
	                        mock_appconfig, mock_create_backup, mock_create_session,
	                        mock_create_lock, mock_delete_file, mock_save_to_file,
	                        mock_load_from_file, mock_download_file):
		"""Test sync with load_only=True."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		mock_download_file.return_value = True
		
		notify_cb = Mock()
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			dbsync.sync(load_only=True, notify_cb=notify_cb)
		
		# Verify download happened
		mock_download_file.assert_called_once()
		
		# Verify load happened
		mock_load_from_file.assert_called_once()
		
		# Verify upload did NOT happen (load_only=True)
		mock_client.files_upload.assert_not_called()
		
		# Verify lock was removed
		assert mock_delete_file.call_args_list[-1][0][1] == dbsync.LOCK_PATH
	
	@patch('wxgtd.model.dbsync.download_file')
	@patch('wxgtd.model.dbsync.loader.load_from_file')
	@patch('wxgtd.model.dbsync.exporter.save_to_file')
	@patch('wxgtd.model.dbsync._delete_file')
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('builtins.open', new_callable=mock_open, read_data=b'sync data')
	@patch('os.unlink')
	def test_sync_full_bidirectional(self, mock_unlink, mock_file_open, mock_dropbox_module,
	                                 mock_appconfig, mock_create_backup, mock_create_session,
	                                 mock_create_lock, mock_delete_file, mock_save_to_file,
	                                 mock_load_from_file, mock_download_file):
		"""Test full bidirectional sync."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		mock_download_file.return_value = True
		
		notify_cb = Mock()
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			dbsync.sync(load_only=False, notify_cb=notify_cb)
		
		# Verify download happened
		mock_download_file.assert_called_once()
		
		# Verify load happened
		mock_load_from_file.assert_called_once()
		
		# Verify export happened
		mock_save_to_file.assert_called_once()
		
		# Verify old file was deleted before upload
		assert any(call[0][1] == dbsync.SYNC_PATH for call in mock_delete_file.call_args_list)
		
		# Verify upload happened
		mock_client.files_upload.assert_called_once()
		upload_args = mock_client.files_upload.call_args
		assert upload_args[0][1] == dbsync.SYNC_PATH
		
		# Verify lock was removed
		assert mock_delete_file.call_args_list[-1][0][1] == dbsync.LOCK_PATH


class TestNotifyProgress:
	"""Test progress notification."""
	
	@patch('wxgtd.model.dbsync.publisher')
	def test_notify_progress_sends_message(self, mock_publisher):
		"""Test notify progress sends publisher message."""
		dbsync._notify_progress(50, "Test message")
		
		mock_publisher.sendMessage.assert_called_once_with(
			'sync.progress',
			progress=50,
			msg="Test message"
		)
