# -*- coding: utf-8 -*-
""" Setup dropbox account dialog.

Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = """Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025"""
__version__ = "2025-12-03"

import logging
import gettext

import wx
try:
	import dropbox
except ImportError:
	dropbox = None  # pylint: disable=C0103

from wxgtd.wxtools.validators import Validator
from wxgtd.wxtools.validators import v_length as LVALID
from wxgtd.lib.appconfig import AppConfigWrapper

from wxgtd.gui import message_boxes as msg
from ._base_dialog import BaseDialog

_ = gettext.gettext
_LOG = logging.getLogger(__name__)


class DlgDropboxAuth(BaseDialog):
	""" Configure Dropbox account authorization.

	Args:
		parent: parent window
	"""

	def __init__(self, parent):
		BaseDialog.__init__(self, parent, 'dlg_dropbox_auth')
		self._setup()
		self._apply_custom_styling()

	def _create_bindings(self, wnd):
		BaseDialog._create_bindings(self, wnd)
		wnd.Bind(wx.EVT_BUTTON, self._on_ok, self['btn_auth'])
		wnd.Bind(wx.EVT_BUTTON, self._on_btn_app_console, self['btn_app_console'])

	def _apply_custom_styling(self):
		"""Apply custom colors and styling to the dialog."""
		# Style the header panel
		header_panel = self['header_panel']
		if header_panel:
			header_panel.SetBackgroundColour(wx.Colour(74, 144, 226))  # #4A90E2
			header_title = self['header_title']
			if header_title:
				header_title.SetForegroundColour(wx.Colour(255, 255, 255))
			header_subtitle = self['header_subtitle']
			if header_subtitle:
				header_subtitle.SetForegroundColour(wx.Colour(232, 244, 255))
		
		# Style the token input panel
		token_panel = self['token_panel']
		if token_panel:
			token_panel.SetBackgroundColour(wx.Colour(248, 249, 250))  # #F8F9FA
		
		# Style the main dialog background
		self._wnd.SetBackgroundColour(wx.Colour(255, 255, 255))  # White
		
		# Style the Save & Connect button
		btn_auth = self['btn_auth']
		if btn_auth:
			btn_auth.SetBackgroundColour(wx.Colour(39, 174, 96))  # #27AE60
			btn_auth.SetForegroundColour(wx.Colour(255, 255, 255))
		
		# Style the App Console button
		btn_console = self['btn_app_console']
		if btn_console:
			btn_console.SetBackgroundColour(wx.Colour(52, 152, 219))  # #3498DB
			btn_console.SetForegroundColour(wx.Colour(255, 255, 255))

	def _setup(self):
		self._config = config = AppConfigWrapper()
		
		# Setup validators for access token (API v2)
		self['tc_access_token'].SetValidator(Validator(config, 'dropbox/access_token',
			validators=LVALID.NotEmptyValidator(),
			field=_("access token")))
		
		# Setup validators for legacy fields (API v1 - kept for backward compatibility)
		self['tc_app_key'].SetValidator(Validator(config, 'dropbox/appkey',
			field=_("app key")))
		self['tc_app_secret'].SetValidator(Validator(config,
			'dropbox/appsecret',
			field=_("app secret")))

	def _on_ok(self, _evt):
		if not self._wnd.Validate():
			return
		if not self._wnd.TransferDataFromWindow():
			return
		
		# For API v2, we don't need the auth flow - just save the token
		access_token = self._config.get('dropbox', 'access_token')
		if access_token:
			# Validate the token by creating a Dropbox instance
			if self._validate_token(access_token):
				self._wnd.EndModal(wx.ID_OK)
				return
		else:
			msg.message_box_error(self._wnd, 
				_("Please enter a valid Dropbox access token"))
	
	def _validate_token(self, access_token):
		"""Validate the Dropbox access token."""
		if dropbox is None:
			msg.message_box_error(self._wnd,
				_("Dropbox SDK is not installed"))
			return False
		
		try:
			dbx = dropbox.Dropbox(access_token)
			account_info = dbx.users_get_current_account()
			# Save account display name for reference
			self._config.set('dropbox', 'info', account_info.name.display_name)
			msg.message_box_info(self._wnd,
				_("Successfully connected to Dropbox account: %s") % 
				account_info.name.display_name)
			return True
		except dropbox.exceptions.AuthError as error:
			_LOG.error('Invalid access token: %r', error)
			msg.message_box_error(self._wnd,
				_("Invalid access token. Please check and try again."))
			return False
		except Exception as error:
			_LOG.exception('Error validating token')
			msg.message_box_error(self._wnd,
				_("Error connecting to Dropbox: %s") % str(error))
			return False

	def _on_btn_app_console(self, _evt):  # pylint: disable=R0201
		wx.LaunchDefaultBrowser('https://www.dropbox.com/developers/apps/create')

	def _auth(self):
		"""Legacy authentication method for API v1 (deprecated)."""
		if dropbox is None:
			return False
		sess = dropbox.session.DropboxSession(
				self._appconfig.get('dropbox', 'appkey'),
				self._appconfig.get('dropbox', 'appsecret'), 'dropbox')
		request_token = sess.obtain_request_token()
		while True:
			try:
				access_token = sess.obtain_access_token(request_token)
				_LOG.debug(access_token)
			except dropbox.rest.ErrorResponse as error:
				_LOG.info('_auth error: %r', error)
				url = sess.build_authorize_url(request_token)
				wx.LaunchDefaultBrowser(url)
				if not msg.message_box_question(self._wnd,
						_("Allow wxGTD to access Dropbox files"),
						_("Please authorize application in Dropbox.")):
					return False
			else:
				self._appconfig.set('dropbox', 'oauth_key', access_token.key)
				self._appconfig.set('dropbox', 'oauth_secret', access_token.secret)
				db_client = dropbox.client.DropboxClient(sess)
				self._appconfig.set('dropbox', 'info',
						db_client.account_info()["display_name"])
				return bool(db_client)


