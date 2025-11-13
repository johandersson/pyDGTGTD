#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Startup application in normal (GUI) mode.

Copyright (c) Karol Będkowski, 2013

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = "Copyright (c) Karol Będkowski, 2013"
__version__ = "2013-03-02"

# Initialize pypubsub with arg1 protocol BEFORE any imports
try:
	from pubsub import setuparg1
except ImportError:
	pass  # pypubsub not installed

from wxgtd.main import run

if __name__ == "__main__":
	run()
