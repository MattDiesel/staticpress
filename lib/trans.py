
import sys, os, os.path, fnmatch, filecmp, shutil, tempfile, configparser

from HTMLReplacements import *
from TransParser import *
from ReplLog import *


class trans:
	def __init__(self, dir, path, conf, rep):
		self.dir = dir
		self.path = path
		self.config = conf
		self.reps = rep

	def htmlrepl(self, file):
		try:
			path, f = os.path.split(file)
			name, ext = os.path.splitext(f)
			cachefile = os.path.join(self.path['cache'], file)
			cachepath = os.path.join(self.path['cache'], path)

			tmpfile = os.path.join(self.tmp, f)

			if (not os.path.exists(cachepath)):
				os.makedirs(cachepath)

			out = open(tmpfile, 'wt', encoding="utf-8")
			parser = TransParser(False, self.reps, out)
			parser.feedf(file)
			out.close()

			if (os.path.exists(cachefile) and filecmp.cmp(tmpfile, cachefile, False)):
				return 'nochange'

			shutil.copy2(tmpfile, cachefile)

			return 'success'
		except Exception as e:
			if configDebug:
				raise

			return type(e).__name__

	def redir(self, file):
		try:
			path, f = os.path.split(file)
			name, ext = os.path.splitext(f)
			cachefile = os.path.join(self.path['cache'], 'index.php')

			tmpfile = os.path.join(self.tmp, 'index.php')

			if (not os.path.exists(self.path['cache'])):
				os.makedirs(self.path['cache'])

			inp = open(file, 'rt')
			p = inp.read(None)
			inp.close()

			out = open(tmpfile, 'wt', encoding="utf-8")
			out.write("<?php header('location:{}'); ?>".format(p))
			out.close()

			if (os.path.exists(cachefile) and filecmp.cmp(tmpfile, cachefile, False)):
				return 'nochange'

			shutil.copy2(tmpfile, cachefile)

			return 'success'
		except Exception as e:
			if configDebug:
				raise

			return type(e).__name__

	def meta(self, file):
		try:
			path, f = os.path.split(file)
			name, ext = os.path.splitext(f)
			cachefile = os.path.join(self.path['cache'], path, '.htaccess')
			cachepath = os.path.join(self.path['cache'], path)

			tmpfile = os.path.join(self.tmp, '.htaccess')

			if (not os.path.exists(cachepath)):
				os.makedirs(cachepath)

			meta = configparser.ConfigParser()
			meta.read(file)

			out = open(tmpfile, 'wt', encoding="utf-8")

			for sect in meta.sections():
				if (sect == 'password'):
					user = meta.get(sect, 'user', os.getlogin())
					pw = meta[sect]['pass']

					# Not Implemented.
				elif (sect == 'listing'):
					enabled = meta.get(sect, 'enable', None)

					if (enabled == None):
						pass
					elif (enabled not in ['no', 'n', '0', 'off', 'disable', 'd', 'f', 'false']):
						enabled = True
						out.write("Options +Indexes\n")
					else:
						enabled = False
						out.write("Options -Indexes\n")

					if (enabled or (enabled == None)):
						options = {
							'DefaultIcon': None,
							'HeaderName': None,
							'ReadmeName': None,
							'IndexIgnore': None,
							'IndexOrderDefault': None,
						}

						indexoptions = {
							'Charset': None,
							'Type': None,
							'DescriptionWidth': None,
							'FancyIndexing': None,
							'FoldersFirst': None,
							'HTMLTable': None,
							'IconsAreLinks': None,
							'IconHeight': None,
							'IconWidth': None,
							'IgnoreCase': None,
							'IgnoreClient': None,
							'NameWidth': None,
							'ScanHTMLTitles': None,
							'SuppressColumnSorting': None,
							'SuppressDescription': None,
							'SuppressHTMLPreamble': None,
							'SuppressIcon': None,
							'SuppressLastModified': None,
							'SuppressRules': None,
							'SuppressSize': None,
							'TrackModified': None,
							'VersionSort': None,
							'XHTML': None,
						}

						for (key,val) in meta[sect]:
							if key in options.keys():
								if val != '':
									options[key] = val
							elif key in indexoptions.keys():
								if val in ['no', 'n', '0', 'off', 'disable', 'd', 'f', 'false']:
									indexoptions[key] = False
								elif val != '':
									indexoptions[key] = True

						indexstr = []
						for (key,val) in indexoptions:
							if val != None:
								indexstr.append('{}{}'.format('+' if val else '-', key))

						if len(indexstr) > 0:
							options['IndexOptions'] = ' '.join(indexstr)

						for (key,val) in options:
							if val != None:
								out.write('{} {}\n'.format(key, val))
				elif (sect == 'listing_desc'):
					for (key,val) in meta[sect]:
						out.write('Description "{}" "{}"\n'.format(val, key))
				elif (sect == 'listing_icons'):
					for (key,val) in meta[sect]:
						if (val[0] == '.'):
							out.write('AddIcon {1} .{0} \n'.format(key[1:], val))
						elif (val[0:4] == 'enc-'):
							out.write('AddIconByEncoding {1} {0}'.format(key[4:], val))
						else:
							out.write('AddIconByType {1} {0}'.format(key[4:], val))

			out.close()

			if (os.path.exists(cachefile) and filecmp.cmp(tmpfile, cachefile, False)):
				return 'nochange'

			shutil.copy2(tmpfile, cachefile)

			return 'success'
		except Exception as e:
			if configDebug:
				raise

			return type(e).__name__

	def copy(self, file):
		try:
			path, f = os.path.split(file)
			name, ext = os.path.splitext(f)

			cachefile = os.path.join(self.path['cache'], file)
			cachepath = os.path.join(self.path['cache'], path)

			if (not os.path.exists(cachepath)):
				os.makedirs(cachepath)
			elif (not os.path.exists(cachefile)):
				pass
			else:
				if (filecmp.cmp(file, cachefile, False)):
					return 'nochange'

			shutil.copy2(file, cachefile)
			return 'success'
		except Exception as e:
			if configDebug:
				raise

			return type(e).__name__

	def traverse(self, dir='.', ignore=['__pycache__']):
		for d in os.listdir(dir):
			path = os.path.relpath(os.path.join(dir, d))

			if ((d in ignore) or (d[0:1] == '.')):
				pass
			elif (os.path.isdir(path)):
				self.traverse(os.path.relpath(path), ignore)
			else:
				name, ext = os.path.splitext(d)
				result = ''
				action = ''

				print(d, "...", end='')

				if (fnmatch.fnmatch(d, '*.html')):
					action = 'translate'
					result = self.htmlrepl(path)
				elif (fnmatch.fnmatch(d, '.redirect')):
					action = 'redirect'
					result = self.redir(path)
				else:
					action = 'copy'
					result = self.copy(path)

				print("(", action, ") -> ", result, sep='')
				self.log.write(path, action, result)

	def run(self):
		self.configDebug = None
		if 'common' in self.config:
			self.configDebug = self.config['common'].get('debug', 'enable')

		if (self.configDebug != None) and (self.configDebug in ['yes', 'y', '1', 'on', 'enable', 'e', 't', 'true']):
			self.configDebug = True
		else:
			self.configDebug = False

		self.log = Log('gen', self.path['logs'])

		if (not os.path.exists(self.path['tmp'])):
			os.makedirs(self.path['tmp'])

		with tempfile.TemporaryDirectory(dir=self.path['tmp']) as self.tmp:
			os.chdir(self.path['www'])
			self.traverse()

		if not '*:success' in self.log.counters.keys():
			print('No changes made.')
		else:
			print('{} Changes made.'.format(self.log.counters['*:success']))

		self.log.end()