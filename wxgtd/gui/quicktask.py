# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904, C0103
""" Quick Task actions.

Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = """Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025"""
__version__ = "2025-12-03"

import gettext
import logging

import wx

from wxgtd.wxtools.wxpub import publisher

from wxgtd.logic import quicktask

_ = gettext.gettext
_LOG = logging.getLogger(__name__)


def quick_task(parent_wnd=None):
	""" Show dialog for quickly adding task. """
	dlg = wx.TextEntryDialog(parent_wnd, _("Enter task title"),
			_("wxGTD Quick Task"), "")
	if dlg.ShowModal() == wx.ID_OK and dlg.GetValue().strip():
		task_uuid = quicktask.create_quicktask(dlg.GetValue().strip())
		publisher.sendMessage('task.update', task_uuid=task_uuid)
	dlg.Destroy()

