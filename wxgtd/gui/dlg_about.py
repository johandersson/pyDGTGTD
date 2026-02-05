#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
""" About dialog.

Copyright (c) Karol Będkowski, 2009-2013
Copyright (c) Johan Andersson, 2025

This file is part of wxGTD
Licence: GPLv2+
"""

__author__ = "Karol Będkowski"
__copyright__ = """Copyright (c) Karol Będkowski, 2009-2013
Copyright (c) Johan Andersson, 2025"""
__version__ = "2025-02-05"
__all__ = ['show_about_box']


import wx
import wx.adv
import wx.lib.agw.hyperlink as hl

from wxgtd import version


class ModernAboutDialog(wx.Dialog):
	""" Modern, beautifully formatted About dialog. """
	
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, "About " + version.NAME,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		
		self.SetBackgroundColour(wx.WHITE)
		self.SetSize((600, 700))
		self.CenterOnParent()
		
		# Main sizer
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Header section with gradient-like background
		header_panel = wx.Panel(self, -1)
		header_panel.SetBackgroundColour(wx.Colour(45, 125, 210))  # Modern blue
		header_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Application name
		app_name = wx.StaticText(header_panel, -1, version.NAME)
		font = wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_BOLD, False, 'Segoe UI')
		app_name.SetFont(font)
		app_name.SetForegroundColour(wx.WHITE)
		header_sizer.Add(app_name, 0, wx.ALIGN_CENTER | wx.TOP, 30)
		
		# Version
		version_text = wx.StaticText(header_panel, -1, 
			"Version " + version.VERSION + " (" + version.RELEASE + ")")
		font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		version_text.SetFont(font)
		version_text.SetForegroundColour(wx.Colour(220, 240, 255))
		header_sizer.Add(version_text, 0, wx.ALIGN_CENTER | wx.TOP, 8)
		
		# Description
		desc_text = wx.StaticText(header_panel, -1, version.DESCRIPTION)
		font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, 
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		desc_text.SetFont(font)
		desc_text.SetForegroundColour(wx.Colour(230, 245, 255))
		header_sizer.Add(desc_text, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 15)
		
		header_panel.SetSizer(header_sizer)
		main_sizer.Add(header_panel, 0, wx.EXPAND)
		
		# Content area with padding
		content_panel = wx.Panel(self, -1)
		content_panel.SetBackgroundColour(wx.WHITE)
		content_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Copyright section
		copyright_label = self._create_section_label(content_panel, "Copyright")
		content_sizer.Add(copyright_label, 0, wx.LEFT | wx.TOP, 20)
		
		copyright_text = wx.StaticText(content_panel, -1, version.COPYRIGHT)
		font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		copyright_text.SetFont(font)
		copyright_text.SetForegroundColour(wx.Colour(80, 80, 80))
		content_sizer.Add(copyright_text, 0, wx.LEFT | wx.TOP, 20)
		
		# Developers section
		dev_label = self._create_section_label(content_panel, "Developers")
		content_sizer.Add(dev_label, 0, wx.LEFT | wx.TOP, 20)
		
		for developer in version.DEVELOPERS.splitlines():
			dev_text = wx.StaticText(content_panel, -1, "• " + developer)
			font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
				wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
			dev_text.SetFont(font)
			dev_text.SetForegroundColour(wx.Colour(60, 60, 60))
			content_sizer.Add(dev_text, 0, wx.LEFT | wx.TOP, 20)
		
		# Links section
		links_label = self._create_section_label(content_panel, "Project Links")
		content_sizer.Add(links_label, 0, wx.LEFT | wx.TOP, 20)
		
		# GitHub link
		github_link = hl.HyperLinkCtrl(content_panel, -1, 
			"GitHub Repository",
			URL="https://github.com/johandersson/pyWeeklyReview")
		font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		github_link.SetFont(font)
		github_link.SetColours(wx.Colour(45, 125, 210), wx.Colour(25, 85, 170),
			wx.Colour(25, 85, 170))
		github_link.EnableRollover(True)
		github_link.SetUnderlines(False, False, True)
		github_link.AutoBrowse(True)
		github_link.DoPopup(False)
		content_sizer.Add(github_link, 0, wx.LEFT | wx.TOP, 20)
		
		# DGT GTD Android link
		android_link = hl.HyperLinkCtrl(content_panel, -1,
			"Compatible with DGT GTD Android App",
			URL="https://www.dgtale.ch/")
		android_link.SetFont(font)
		android_link.SetColours(wx.Colour(45, 125, 210), wx.Colour(25, 85, 170),
			wx.Colour(25, 85, 170))
		android_link.EnableRollover(True)
		android_link.SetUnderlines(False, False, True)
		android_link.AutoBrowse(True)
		android_link.DoPopup(False)
		content_sizer.Add(android_link, 0, wx.LEFT | wx.TOP, 8)
		
		# License section
		license_label = self._create_section_label(content_panel, "License")
		content_sizer.Add(license_label, 0, wx.LEFT | wx.TOP, 20)
		
		license_text = wx.TextCtrl(content_panel, -1, version.LICENSE,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_SIMPLE)
		font = wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_NORMAL, False, 'Consolas')
		license_text.SetFont(font)
		license_text.SetBackgroundColour(wx.Colour(248, 248, 248))
		license_text.SetForegroundColour(wx.Colour(70, 70, 70))
		content_sizer.Add(license_text, 1, wx.EXPAND | wx.ALL, 20)
		
		content_panel.SetSizer(content_sizer)
		main_sizer.Add(content_panel, 1, wx.EXPAND)
		
		# Button area
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		close_btn = wx.Button(self, wx.ID_OK, "Close")
		close_btn.SetDefault()
		font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')
		close_btn.SetFont(font)
		button_sizer.Add(close_btn, 0, wx.ALL, 10)
		
		main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		
		self.SetSizer(main_sizer)
		self.Layout()
	
	def _create_section_label(self, parent, text):
		""" Create a styled section label. """
		label = wx.StaticText(parent, -1, text)
		font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
			wx.FONTWEIGHT_BOLD, False, 'Segoe UI')
		label.SetFont(font)
		label.SetForegroundColour(wx.Colour(45, 125, 210))
		return label


def show_about_box(parent):
	""" Create and show modern about dialog. """
	dlg = ModernAboutDialog(parent)
	dlg.ShowModal()
	dlg.Destroy()


