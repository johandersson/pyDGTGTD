#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Functions for synchronisation data between database and sync file.

Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = """Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025"""
__version__ = "2025-12-03"


import os
import logging
import gettext
import tempfile
import datetime

try:
	import cjson
	_JSON_DECODER = cjson.decode
	_JSON_ENCODER = cjson.encode
except ImportError:
	import json
	_JSON_DECODER = json.loads
	_JSON_ENCODER = json.dumps

try:
	import dropbox
	from dropbox import DropboxOAuth2FlowNoRedirect
	from dropbox.exceptions import ApiError, AuthError
except ImportError:
	dropbox = None  # pylint: disable=C0103
	DropboxOAuth2FlowNoRedirect = None
	ApiError = None
	AuthError = None

from wxgtd.wxtools.wxpub import publisher

from wxgtd.lib import appconfig
from wxgtd.lib import ignore_exceptions

from wxgtd.model import exporter
from wxgtd.model import loader
from wxgtd.model import sync as SYNC
from wxgtd.model import objects


_LOG = logging.getLogger(__name__)
_ = gettext.gettext


SYNC_PATH = '/Apps/DGT-GTD/sync/GTD_SYNC.zip'
LOCK_PATH = '/Apps/DGT-GTD/sync/sync.locked'


def is_available():
	return bool(dropbox)


def _notify_progress(progress, msg):
	publisher.sendMessage('sync.progress', progress=progress, msg=msg)


def _create_session():
	"""Create Dropbox client using API v2 with OAuth2 access token."""
	appcfg = appconfig.AppConfig()
	access_token = appcfg.get('dropbox', 'access_token')
	if not access_token:
		# Fall back to old oauth_key for backward compatibility
		access_token = appcfg.get('dropbox', 'oauth_key')
	if not access_token:
		raise SYNC.OtherSyncError(_("Dropbox access token not configured."))
	return dropbox.Dropbox(access_token)


def download_file(fileobj, source, dbclient):
	_LOG.info('download_file')
	try:
		metadata, response = dbclient.files_download(source)
		if metadata and metadata.size > 0:
			fileobj.write(response.content)
			return True
	except ApiError as err:
		_LOG.warning("download_file: %r not found - %s", source, err)
	return False


def _delete_file(dbclient, path):
	try:
		dbclient.files_delete_v2(path)
	except ApiError as error:
		_LOG.warning('_delete_file(%s) error: %s', path, error)


def sync(load_only=False, notify_cb=_notify_progress):
	""" Sync data from/to given file.

	Notify progress by publisher.

	Args:
		load_only: only load, not write data

	Raises:
		SyncLockedError when source file is locked.
	"""
	_LOG.info("sync: %r", SYNC_PATH)
	if not dropbox:
		raise SYNC.OtherSyncError(_("Dropbox is not available."))
	appcfg = appconfig.AppConfig()
	if not appcfg.get('dropbox', 'access_token') and not appcfg.get('dropbox', 'oauth_key'):
		raise SYNC.OtherSyncError(_("Dropbox is not configured."))
	notify_cb(0, _("Sync via Dropbox API v2...."))
	notify_cb(1, _("Creating backup"))
	SYNC.create_backup()
	notify_cb(25, _("Checking sync lock"))
	try:
		dbclient = _create_session()
	except (ApiError, AuthError) as error:
		raise SYNC.OtherSyncError(_("Dropbox: connection failed: %s") %
				str(error))
	temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
	temp_filename = temp_file.name
	if create_sync_lock(dbclient):
		notify_cb(2, _("Downloading..."))
		try:
			loaded = download_file(temp_file, SYNC_PATH, dbclient)
			temp_file.close()
			if loaded:
				loader.load_from_file(temp_filename, notify_cb)
			if not load_only:
				exporter.save_to_file(temp_filename, notify_cb, 'GTD_SYNC.json')
				_delete_file(dbclient, SYNC_PATH)
				notify_cb(20, _("Uploading..."))
				with open(temp_filename, 'rb') as temp_file:
					dbclient.files_upload(temp_file.read(), SYNC_PATH, mode=dropbox.files.WriteMode('overwrite'))
		except Exception as err:
			_LOG.exception("file sync error")
			raise SYNC.OtherSyncError(err)
		finally:
			notify_cb(90, _("Removing sync lock"))
			_delete_file(dbclient, LOCK_PATH)
			with ignore_exceptions(IOError):
				os.unlink(temp_filename)
		notify_cb(100, _("Completed"))
	else:
		notify_cb(100, _("Synchronization file is locked. "
			"Can't synchronize..."))
		raise SYNC.SyncLockedError()


def create_sync_lock(dbclient):
	""" Check if lockfile exists in sync folder. Create if not.

	Args:
		dbclient: dropbox client session

	Returns:
		False, if directory is locked.
	"""
	try:
		metadata = dbclient.files_get_metadata(LOCK_PATH)
		if metadata and metadata.size > 0:
			return False
	except AuthError as error:
		_LOG.error('Dropbox auth error: %s', error)
		raise SYNC.OtherSyncError(_("Dropbox authentication failed. "
			"Please check your access token and app permissions."))
	except ApiError:
		_LOG.debug('Lock file does not exist, will create it')

	session = objects.Session()
	device_id = session.query(objects.Conf).filter_by(  # pylint: disable=E1101
			key='deviceId').first()
	synclog = {'deviceId': device_id.val,
			"startTime": exporter.fmt_date(datetime.datetime.utcnow())}
	session.flush()  # pylint: disable=E1101
	synclog_data = _JSON_ENCODER(synclog).encode('utf-8')
	dbclient.files_upload(synclog_data, LOCK_PATH, mode=dropbox.files.WriteMode('overwrite'))
	return True

