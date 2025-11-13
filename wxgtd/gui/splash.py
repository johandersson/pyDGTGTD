# -*- coding: utf-8 -*-
""" Splash screen window.

Copyright (c) Karol Będkowski, 2013

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2010-2013"
__version__ = "2013-04-28"


import wx
import wx.adv

from wxgtd import version
from wxgtd.lib.appconfig import AppConfig


class Splash(wx.adv.SplashScreen):
	""" Splash Screen class. """

	def __init__(self):
		config = AppConfig()
		splash_img = wx.Image(config.get_data_file('splash.png'))
		wx.adv.SplashScreen.__init__(self, splash_img.ConvertToBitmap(),
			wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
			2000, None, -1)

		# In wxPython Phoenix (4.x), use self instead of GetSplashWindow()
		ver = wx.StaticText(self, -1, version.VERSION, pos=(330, 170))
		ver.SetBackgroundColour(wx.WHITE)
