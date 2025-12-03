# -*- coding: utf-8 -*-
""" wxGTD main module.

Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

# Initialize pypubsub with arg1 protocol before any other imports
# This must happen before wx is imported anywhere
try:
	from pubsub import setuparg1
except ImportError:
	pass  # pypubsub not installed, will fall back to wx.lib.pubsub

