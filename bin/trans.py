
import sys, os, os.path, fnmatch, filecmp, shutil, tempfile, configparser

basepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.insert(0, os.path.join(basepath, 'lib'))

from HTMLReplacements import *
from TransParser import *
from repllog import *

sys.path.pop(0)

basedir = os.getcwd()
cachedir = 'cache'
tempdir = 'tmp'
configdir = 'config'
temppath = os.path.join(basedir, tempdir)

def htmlrepl(file):
	try:
		path, f = os.path.split(file)
		name, ext = os.path.splitext(f)

		cachepath = os.path.join(cachedir, path[4:])
		cachefile = os.path.join(cachepath, f)

		tmpfile = os.path.join(tmp, f)

		if (not os.path.exists(cachepath)):
			os.makedirs(cachepath)

		out = open(tmpfile, 'wt', encoding="utf-8")
		parser = TransParser(False, reps, out)
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

def redir(file):
	try:
		path, f = os.path.split(file)
		name, ext = os.path.splitext(f)

		cachepath = os.path.join(cachedir, path[4:])
		cachefile = os.path.join(cachepath, 'index.php')

		tmpfile = os.path.join(tmp, 'index.php')

		if (not os.path.exists(cachepath)):
			os.makedirs(cachepath)

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

def meta(file):
	try:
		path, f = os.path.split(file)
		name, ext = os.path.splitext(f)

		cachepath = os.path.join(cachedir, path[4:])
		cachefile = os.path.join(cachepath, '.htaccess')

		tmpfile = os.path.join(tmp, '.htaccess')

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

def copy(file):
	try:
		path, f = os.path.split(file)
		name, ext = os.path.splitext(f)

		cachepath = os.path.join(cachedir, path[4:])
		cachefile = os.path.join(cachepath, f)

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
		return type(e).__name__

def traverse(dir='www', ignore=['__pycache__']):
	for d in os.listdir(dir):
		path = '{}/{}'.format(dir, d)

		if ((d in ignore) or (d[0:1] == '.')):
			pass
		elif (os.path.isdir(path)):
			traverse(path, ignore)
		else:
			name, ext = os.path.splitext(d)
			result = ''
			action = ''

			print(d, "...", end='')

			if (fnmatch.fnmatch(d, '*.html')):
				action = 'translate'
				result = htmlrepl(path)
			elif (fnmatch.fnmatch(d, '.redirect')):
				action = 'redirect'
				result = redir(path)
			else:
				action = 'copy'
				result = copy(path)

			print("(", action, ") -> ", result, sep='')
			log.write(path, action, result)

config = configparser.ConfigParser()
config.read(os.path.join(basedir, configdir, 'default.conf'))
configDebug = config.get('debug', 'enable')
if (configDebug != None) and (configDebug in ['yes', 'y', '1', 'on', 'enable', 'e', 't', 'true']):
	configDebug = True
else:
	configDebug = False

log = Log()
reps = HTMLReplacements('tags')

if (not os.path.exists(temppath)):
	os.makedirs(temppath)

with tempfile.TemporaryDirectory(dir=temppath) as tmp:
	traverse()

if not '*:success' in log.counters.keys():
	print('No changes made')
else:
	print('{} Changes made.'.format(log.counters['*:success']))

log.end()