#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Standard paths.

Copyright (c) Karol Będkowski, 2004-2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = """Copyright (c) Karol Będkowski, 2013
Copyright (c) Johan Andersson, 2025"""
__version__ = "2025-12-03"


from wxgtd import version

LINUX_LOCALES_DIR = 'share/locale'
LINUX_INSTALL_DIR = 'share/%s' % version.SHORTNAME
LINUX_DOC_DIR = 'share/doc/%s' % version.SHORTNAME
LINUX_DATA_DIR = 'share/%s/data' % version.SHORTNAME


LOCALES_DIR = './locale'
DATA_DIR = './data'

