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


# Import dropbox exceptions if available
try:
    from dropbox.exceptions import ApiError, AuthError, RateLimitError
except ImportError:
    ApiError = None
    AuthError = None
    RateLimitError = None


class MockDropboxMetadata:
	"""Mock Dropbox file metadata."""
	def __init__(self, size=100):
		self.size = size


class MockDropboxResponse:
	"""Mock Dropbox file download response."""
	def __init__(self, content=b"test content"):
		self.content = content


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
		# This test is environment-dependent - skip if dropbox is not available
		if dbsync.dropbox is None:
			pytest.skip("Dropbox not installed in test environment")
		assert dbsync.is_available() is True
	
	@patch('wxgtd.model.dbsync.dropbox', None)
	def test_is_available_when_dropbox_not_installed(self):
		"""Test that is_available returns False when dropbox is not installed."""
		assert dbsync.is_available() is False


class TestCreateSession:
	"""Test Dropbox session creation."""
	
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_with_access_token(self, mock_appconfig, mock_dropbox_module):
		"""Test session creation with access token."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_access_token'
		mock_appconfig.return_value = mock_config
		
		dbsync._create_session()
		
		mock_config.get.assert_any_call('dropbox', 'access_token')
		mock_dropbox_module.Dropbox.assert_called_once_with('test_access_token')
	
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_fallback_to_oauth_key(self, mock_appconfig, mock_dropbox_module):
		"""Test session creation falls back to oauth_key if access_token not set."""
		mock_config = MagicMock()
		mock_config.get.side_effect = lambda section, key: {
			('dropbox', 'access_token'): None,
			('dropbox', 'oauth_key'): 'old_oauth_key'
		}.get((section, key))
		mock_appconfig.return_value = mock_config
		
		dbsync._create_session()
		
		mock_dropbox_module.Dropbox.assert_called_once_with('old_oauth_key')
	
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
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
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
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
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
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		
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


class TestEdgeCases:
	"""Test edge cases and error conditions for Dropbox sync."""
	
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_with_invalid_token(self, mock_appconfig, mock_dropbox_module):
		"""Test session creation with invalid access token."""
		if AuthError is None:
			pytest.skip("Dropbox not available")
		
		mock_config = MagicMock()
		mock_config.get.return_value = 'invalid_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_client.users_get_current_account.side_effect = AuthError(
			request_id='123',
			error='invalid_access_token'
		)
		mock_dropbox_module.Dropbox.return_value = mock_client
		
		# This should still return the client - validation happens later
		result = dbsync._create_session()
		assert result is not None
	
	@patch('wxgtd.model.dbsync.dropbox')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	def test_create_session_network_error(self, mock_appconfig, mock_dropbox_module):
		"""Test session creation with network connectivity issues."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_client.users_get_current_account.side_effect = ApiError(
			request_id='123',
			error='network_error',
			user_message_text='Network connection failed'
		)
		mock_dropbox_module.Dropbox.return_value = mock_client
		
		# This should still return the client - validation happens later
		result = dbsync._create_session()
		assert result is not None
	
	def test_download_file_corrupted_data(self):
		"""Test download with corrupted/incomplete data."""
		mock_client = MagicMock()
		mock_metadata = MockDropboxMetadata(size=100)
		# Simulate corrupted content (shorter than metadata.size)
		mock_response = MockDropboxResponse(content=b"short")
		mock_client.files_download.return_value = (mock_metadata, mock_response)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		# Should still return True as long as some data was written
		assert result is True
		assert len(fileobj.getvalue()) == 5
	
	def test_download_file_large_file(self):
		"""Test download of large file."""
		mock_client = MagicMock()
		large_content = b"x" * (10 * 1024 * 1024)  # 10MB
		mock_metadata = MockDropboxMetadata(size=len(large_content))
		mock_response = MockDropboxResponse(content=large_content)
		mock_client.files_download.return_value = (mock_metadata, mock_response)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/large.zip', mock_client)
		
		assert result is True
		assert len(fileobj.getvalue()) == len(large_content)
	
	def test_download_file_rate_limit_error(self):
		"""Test download with rate limit exceeded error."""
		if ApiError is None or RateLimitError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_download.side_effect = RateLimitError(
			request_id='123',
			error='too_many_requests',
			retry_after=60
		)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		assert result is False
	
	def test_download_file_permission_error(self):
		"""Test download with insufficient permissions."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_download.side_effect = ApiError(
			request_id='123',
			error='insufficient_permissions',
			user_message_text='Access denied'
		)
		
		fileobj = BytesIO()
		result = dbsync.download_file(fileobj, '/test/path.zip', mock_client)
		
		assert result is False
	
	def test_delete_file_rate_limit_error(self):
		"""Test delete file with rate limit error."""
		if RateLimitError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_delete_v2.side_effect = RateLimitError(
			request_id='123',
			error='too_many_requests',
			retry_after=30
		)
		
		# Should not raise exception, just log warning
		dbsync._delete_file(mock_client, '/test/path.zip')
		
		mock_client.files_delete_v2.assert_called_once_with('/test/path.zip')
	
	def test_delete_file_permission_denied(self):
		"""Test delete file with permission denied."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_delete_v2.side_effect = ApiError(
			request_id='123',
			error='insufficient_permissions',
			user_message_text='Permission denied'
		)
		
		# Should not raise exception, just log warning
		dbsync._delete_file(mock_client, '/test/path.zip')
		
		mock_client.files_delete_v2.assert_called_once_with('/test/path.zip')


class TestSyncLockEdgeCases:
	"""Test edge cases for sync lock functionality."""
	
	@patch('wxgtd.model.dbsync.objects.Session')
	def test_create_sync_lock_database_error(self, mock_session_class):
		"""Test sync lock creation when database query fails."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		
		# Simulate lock file not existing
		mock_client.files_get_metadata.side_effect = ApiError(
			request_id='123',
			error=None,
			user_message_text='Not found'
		)
		
		# Mock database error
		mock_session = MagicMock()
		mock_session.query.side_effect = Exception("Database connection failed")
		mock_session_class.return_value = mock_session
		
		result = dbsync.create_sync_lock(mock_client)
		
		assert result is False
		mock_client.files_upload.assert_not_called()
	
	@patch('wxgtd.model.dbsync.objects.Session')
	@patch('wxgtd.model.dbsync.exporter.fmt_date')
	def test_create_sync_lock_device_id_not_found(self, mock_fmt_date, mock_session_class):
		"""Test sync lock creation when device ID is not found in database."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		
		# Simulate lock file not existing
		mock_client.files_get_metadata.side_effect = ApiError(
			request_id='123',
			error=None,
			user_message_text='Not found'
		)
		
		# Mock device ID not found
		mock_session = MagicMock()
		mock_session.query.return_value.filter_by.return_value.first.return_value = None
		mock_session_class.return_value = mock_session
		
		result = dbsync.create_sync_lock(mock_client)
		
		assert result is False
		mock_client.files_upload.assert_not_called()
	
	def test_create_sync_lock_auth_error(self):
		"""Test sync lock creation with authentication error."""
		if AuthError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_get_metadata.side_effect = AuthError(
			request_id='123',
			error='expired_access_token'
		)
		
		with pytest.raises(SYNC.OtherSyncError, match="authentication failed"):
			dbsync.create_sync_lock(mock_client)
	
	def test_create_sync_lock_network_error(self):
		"""Test sync lock creation with network error."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		mock_client.files_get_metadata.side_effect = ApiError(
			request_id='123',
			error='network_error',
			user_message_text='Connection timeout'
		)
		
		result = dbsync.create_sync_lock(mock_client)
		
		assert result is False


class TestSyncEdgeCases:
	"""Test edge cases for main sync function."""
	
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_connection_error_during_session_creation(self, mock_dropbox_module,
	                                                       mock_appconfig, mock_create_session):
		"""Test sync when connection fails during session creation."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_create_session.side_effect = ApiError(
			request_id='123',
			error='connection_error',
			user_message_text='Connection failed'
		)
		
		with pytest.raises(SYNC.OtherSyncError, match="connection failed"):
			dbsync.sync()
	
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_download_fails(self, mock_dropbox_module, mock_appconfig,
	                             mock_create_backup, mock_create_session, mock_create_lock):
		"""Test sync when download fails."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		
		notify_cb = Mock()
		
		with patch('wxgtd.model.dbsync.download_file', return_value=False):
			with patch('tempfile.NamedTemporaryFile') as mock_temp:
				mock_temp_file = MagicMock()
				mock_temp_file.name = '/tmp/test.zip'
				mock_temp.return_value = mock_temp_file
				
				# Should complete without error even if download fails
				dbsync.sync(load_only=True, notify_cb=notify_cb)
	
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
	def test_sync_upload_fails(self, mock_file_open, mock_dropbox_module, mock_appconfig,
	                           mock_create_backup, mock_create_session, mock_create_lock,
	                           mock_delete_file, mock_save_to_file, mock_load_from_file,
	                           mock_download_file):
		"""Test sync when upload fails."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_client.files_upload.side_effect = ApiError(
			request_id='123',
			error='upload_failed',
			user_message_text='Upload failed'
		)
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		mock_download_file.return_value = True
		
		notify_cb = Mock()
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			with pytest.raises(SYNC.OtherSyncError):
				dbsync.sync(load_only=False, notify_cb=notify_cb)
	
	@patch('wxgtd.model.dbsync.download_file')
	@patch('wxgtd.model.dbsync.loader.load_from_file')
	@patch('wxgtd.model.dbsync._delete_file')
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_load_from_file_fails(self, mock_dropbox_module, mock_appconfig,
	                                   mock_create_backup, mock_create_session,
	                                   mock_create_lock, mock_delete_file,
	                                   mock_load_from_file, mock_download_file):
		"""Test sync when loading from file fails."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		mock_download_file.return_value = True
		mock_load_from_file.side_effect = Exception("Invalid file format")
		
		notify_cb = Mock()
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			with pytest.raises(SYNC.OtherSyncError):
				dbsync.sync(load_only=True, notify_cb=notify_cb)
	
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_temp_file_cleanup_error(self, mock_dropbox_module, mock_appconfig,
	                                      mock_create_backup, mock_create_session,
	                                      mock_create_lock):
		"""Test sync when temporary file cleanup fails."""
		import os
		
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		
		notify_cb = Mock()
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			with patch('wxgtd.model.dbsync.download_file', return_value=False):
				with patch('os.unlink', side_effect=OSError("Permission denied")):
					# Should complete despite cleanup error (wrapped in ignore_exceptions)
					dbsync.sync(load_only=True, notify_cb=notify_cb)
	
	@patch('wxgtd.model.dbsync.create_sync_lock')
	@patch('wxgtd.model.dbsync._create_session')
	@patch('wxgtd.model.dbsync.SYNC.create_backup')
	@patch('wxgtd.model.dbsync.appconfig.AppConfig')
	@patch('wxgtd.model.dbsync.dropbox')
	def test_sync_notify_callback_error(self, mock_dropbox_module, mock_appconfig,
	                                    mock_create_backup, mock_create_session,
	                                    mock_create_lock):
		"""Test sync when notify callback raises exception."""
		mock_config = MagicMock()
		mock_config.get.return_value = 'test_token'
		mock_appconfig.return_value = mock_config
		
		mock_client = MagicMock()
		mock_create_session.return_value = mock_client
		mock_create_lock.return_value = True
		
		notify_cb = Mock(side_effect=Exception("Callback failed"))
		
		with patch('tempfile.NamedTemporaryFile') as mock_temp:
			mock_temp_file = MagicMock()
			mock_temp_file.name = '/tmp/test.zip'
			mock_temp.return_value = mock_temp_file
			
			with patch('wxgtd.model.dbsync.download_file', return_value=False):
				# Should raise exception from callback
				with pytest.raises(Exception, match="Callback failed"):
					dbsync.sync(load_only=True, notify_cb=notify_cb)


class TestConcurrentSync:
	"""Test concurrent sync scenarios."""
	
	@patch('wxgtd.model.dbsync.objects.Session')
	@patch('wxgtd.model.dbsync.exporter.fmt_date')
	def test_concurrent_lock_creation_race_condition(self, mock_fmt_date, mock_session_class):
		"""Test race condition when multiple processes try to create lock simultaneously."""
		if ApiError is None:
			pytest.skip("Dropbox not available")
		
		mock_client = MagicMock()
		
		# First call: file doesn't exist
		# Second call: file exists (created by another process)
		mock_client.files_get_metadata.side_effect = [
			ApiError(request_id='123', error=None, user_message_text='Not found'),
			MagicMock(size=50)  # Lock file exists
		]
		
		# Mock database session
		mock_session = MagicMock()
		mock_conf = MagicMock()
		mock_conf.val = 'device_123'
		mock_session.query.return_value.filter_by.return_value.first.return_value = mock_conf
		mock_session_class.return_value = mock_session
		
		mock_fmt_date.return_value = '2025-12-03T10:00:00Z'
		
		# First attempt should succeed
		result1 = dbsync.create_sync_lock(mock_client)
		assert result1 is True
		
		# Second attempt should fail (already locked)
		result2 = dbsync.create_sync_lock(mock_client)
		assert result2 is False
