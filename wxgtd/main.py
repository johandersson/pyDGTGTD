# -*- coding: utf-8 -*-
""" Main module - gui interface

Copyright (c) Karol Będkowski, 2013

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2013"
__version__ = "2013-04-27"


import os
import argparse
import logging
import sys

_LOG = logging.getLogger(__name__)


from wxgtd import version


def _parse_opt():
	""" Parse cli options. """
	parser = argparse.ArgumentParser(
		prog=version.NAME + " (GUI)",
		description=version.DESCRIPTION
	)
	
	task_group = parser.add_argument_group("Creating tasks")
	task_group.add_argument('--quick-task-dialog', action="store_true", default=False,
			help='show quick task dialog', dest="quick_task_dialog")
	
	debug_group = parser.add_argument_group("Debug options")
	debug_group.add_argument('--debug', '-d', action="store_true", default=False,
			help='enable debug messages')
	debug_group.add_argument('--debug-sql', action="store_true", default=False,
			help='enable sql debug messages')
	debug_group.add_argument('--wx-inspection', action="store_true", default=False,
			help='enable wx inspection tool')
	
	other_group = parser.add_argument_group("Other options")
	other_group.add_argument('--force-start', action="store_true", default=False,
			help='Force start application even if another instance is running.')
	other_group.add_argument('--version', action='version', 
			version=f'{version.NAME} {version.VERSION}')
	
	return parser.parse_args()


def _run_ipcs(config):
	from wxgtd.wxtools import ipc
	ipcs = ipc.IPC(os.path.join(config.config_path, "wxgtd_lock"))
	if not ipcs.startup("gui.frame_main.raise"):
		_LOG.info("App is already running...")
		exit(0)
	return ipcs


def run():
	""" Run application. """
	# parse options
	options = _parse_opt()

	# logowanie
	from wxgtd.lib.logging_setup import logging_setup
	logging_setup('wxgtd.log', options.debug, options.debug_sql)

	# app config
	from wxgtd.lib import appconfig
	config = appconfig.AppConfig('wxgtd.cfg', 'wxgtd')
	config.load_defaults(config.get_data_file('defaults.cfg'))
	config.load()
	config.debug = options.debug

	# import wx (wxversion not needed in wxPython 4.x)
	import wx
	_LOG.info("WX version: %s", wx.version())

	ipcs = None
	if not options.force_start:
		ipcs = _run_ipcs(config)

	# locale
	from wxgtd.lib import locales
	locales.setup_locale(config)

	# create app
	app = wx.App(False)
	if wx.version().startswith('2'):
		wx.InitAllImageHandlers()

	# splash screen
	if not options.quick_task_dialog:
		from wxgtd.gui.splash import Splash
		Splash().Show()
		wx.Yield()

	if sys.platform == 'win32':
		wx.Locale.AddCatalogLookupPathPrefix(config.locales_dir)
		wx.Locale(wx.LANGUAGE_DEFAULT).AddCatalog('wxstd')

	# connect to databse
	from wxgtd.model import db
	db.connect(db.find_db_file(config), options.debug_sql)

	if options.quick_task_dialog:
		from wxgtd.gui import quicktask
		quicktask.quick_task(None)
	else:
		# init icons
		from wxgtd.wxtools import iconprovider
		iconprovider.init_icon_cache(None, config.data_dir)

		# show main window
		from wxgtd.gui.frame_main import FrameMain
		main_frame = FrameMain()
		app.SetTopWindow(main_frame.wnd)
		if not config.get('gui', 'hide_on_start'):
			main_frame.wnd.Show()

		# optionally show inspection tool
		if options.wx_inspection:
			import wx.lib.inspection
			wx.lib.inspection.InspectionTool().Show()

		app.MainLoop()

	# app closed; save config
	if ipcs:
		ipcs.shutdown()
	config.save()
