#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import os.path
import time
import sys

from setuptools import setup, find_packages
from distutils.cmd import Command
import distutils.command.clean

from wxgtd import version, configuration

build = time.asctime()


def find_files(directory, base, filter_func=None):
	for name, subdirs, files in os.walk(directory):
		if files:
			yield (os.path.join(base[:-len(directory)], name),
					[os.path.join(name, fname) for fname
						in filter(filter_func, files)])


def get_data_files():
	if sys.platform == 'win32':
		doc_dir = locales_dir = data_dir = '.'
	else:
		doc_dir = configuration.LINUX_DOC_DIR
		locales_dir = configuration.LINUX_LOCALES_DIR
		data_dir = configuration.LINUX_DATA_DIR
	yield (doc_dir, ['AUTHORS', 'README', "TODO", "COPYING", 'ChangeLog'])
	for x in find_files('data', data_dir):
		yield x
	for x in find_files('locale', locales_dir):
		yield x


def _delete_dir(path):
	if os.path.exists(path):
		for root, dirs, files in os.walk(path, topdown=False):
			for name in files:
				filename = os.path.join(root, name)
				print('Delete', filename)
				os.remove(filename)
			for name in dirs:
				filename = os.path.join(root, name)
				print('Delete dir', filename)
				os.rmdir(filename)
		os.removedirs(path)


class CleanupCmd(distutils.command.clean.clean):
	"""docstring for cleanup"""
	def run(self):
		for root, dirs, files in os.walk('.', topdown=False):
			for name in files:
				nameext = os.path.splitext(name)[-1]
				if (name.endswith('~') or name.startswith('profile_result_')
						or name.endswith('-stamp')
						or nameext in ('.pyd', '.pyc', '.pyo', '.log', '.tmp',
							'.swp', '.db', '.cfg', '.debhelper', '.substvars',
							'.orig')):
					if name in ('defaults.cfg', 'setup.cfg'):
						continue
					filename = os.path.join(root, name)
					print('Delete', filename)
					os.remove(filename)
		_delete_dir('build')
		_delete_dir('debian/wxgtd')
		if os.path.exists('hotshot_edi_stats'):
			os.remove('hotshot_edi_stats')
		distutils.command.clean.clean.run(self)


class UpdatePotfilesCommand(Command):
	"""docstring for cleanup"""

	description = "update POTFILEs.in"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		potfiles = open('po/POTFILES.in', 'wt')
		for line in self._find_files():
			potfiles.write(line + '\n')
		potfiles.close()

	def _find_files(self):
		for root, dirs, files in os.walk('.'):
			if root == '.':
				continue
			if os.path.basename(root).startswith('.'):
				continue
			if root.startswith('./wxgtd_tests'):
				continue
			if root.startswith('./build'):
				continue
			if root.startswith('./debian'):
				continue
			for name in files:
				nameext = os.path.splitext(name)[-1]
				filename = os.path.join(root, name)[2:]
				if nameext == '.xrc':
					yield '[type: gettext/glade] ' + filename
				elif nameext == '.py':
					yield filename


class MakeMoCommand(Command):
	"""docstring for cleanup"""

	description = "create mo files"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		po_langs = (filename[:-3] for filename in os.listdir('po')
				if filename.endswith('.po'))
		for lang in po_langs:
			print('creating mo for', lang)
			path = os.path.join('locale', lang, 'LC_MESSAGES')
			if not os.path.exists(path):
				os.makedirs(path)
			os.spawnlp(os.P_WAIT, 'msgfmt', 'msgfmt', 'po/%s.po' % lang,
					'-o', os.path.join(path, '%s.mo' % version.SHORTNAME))


class MakeManCommand(Command):
	"""docstring for cleanup"""

	description = "create manpages"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		rst_files = (filename[:-4] for filename in os.listdir('man')
				if filename.endswith('.rst'))
		for rst in rst_files:
			print('creating manpage', rst)
			os.spawnlp(os.P_WAIT, 'rst2man', 'rst2man', 'man/%s.rst' % rst,
					'man/%s.1' % rst)
			print('creating html page', rst)
			os.spawnlp(os.P_WAIT, 'rst2html', 'rst2html', 'man/%s.rst' % rst,
					'man/%s.html' % rst)


class MakeXrcCommand(Command):
	"""docstring for cleanup"""

	description = "create xrc files from wxgs"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		wxg_files = (filename[:-4] for filename in os.listdir('data')
				if filename.endswith('.wxg'))
		base_dir = os.path.realpath('data')
		print(base_dir)
		for wxg in wxg_files:
			print('creating', wxg)
			os.spawnlp(os.P_WAIT, 'wxglade', 'wgxglage', '-g', 'XRC', '-o',
					os.path.join(base_dir, '%s.xrc' % wxg),
					os.path.join(base_dir, '%s.wxg' % wxg))


if __name__ == '__main__':
	cmdclass = {'make_mo': MakeMoCommand,
			'make_man': MakeManCommand,
			'update_potfiles': UpdatePotfilesCommand,
			'create_xrc': MakeXrcCommand,
			'clean': CleanupCmd}

	setup(name='wxgtd',
			version=version.VERSION,
			author="Karol Będkowski",
			author_email='karol.bedkowski@gmail.com',
			description="%s - %s (%s, build: %s)"
					% (version.NAME, version.DESCRIPTION, version.RELEASE, build),
			long_description='-',
			license='GPL v2',
			url='-',
			download_url='-',
			classifiers=['Development Status :: 4 - Beta',
				'Environment :: Win32 (MS Windows)',
				'Environment :: X11 Applications',
				'License :: OSI Approved :: GNU General Public License (GPL)',
				'Operating System :: OS Independent',
				'Programming Language :: Python :: 3',
				'Programming Language :: Python :: 3.8',
				'Programming Language :: Python :: 3.9',
				'Programming Language :: Python :: 3.10',
				'Programming Language :: Python :: 3.11',
				'Topic :: Office/Business'],
			packages=find_packages(),
			data_files=list(get_data_files()),
			include_package_data=True,
			install_requires=['wxPython>=4.0.0', 'sqlalchemy>=1.4.0,<2.0.0'],
			python_requires='>=3.8',
			cmdclass=cmdclass,
			test_suite='pytest')

