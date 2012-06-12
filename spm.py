
__NAME__ = 'spm'
__AUTHOR__ = 'Matt Diesel'
__VERSION__ = 'a6'

import sys, os, os.path, logging, configparser, shutil, http.server, socketserver


basepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.insert(0, os.path.join(basepath, 'lib'))

from CmdLine import CmdLine, CmdLineBase, CmdLineError
from HTMLReplacements import HTMLReplacements
from trans import trans
from SPServer import SPServer

sys.path.pop(0)

class SPMError(Exception):
	pass

class SPM(CmdLineBase):
	def __init__(self, dir):
		self.basedir = dir

		self.spbase = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))

		self.dir = {
			'config': 'config',
			'www': 'www',
			'tmp': 'tmp',
			'cache': 'cache',
			'logs': 'logs',
			'tags': 'tags',
		}
		self.path = dict([ (key, os.path.join(self.basedir, val)) for (key, val) in self.dir.items()  ])
		self.sppath = dict([ (key, os.path.join(self.spbase, val)) for (key, val) in self.dir.items()  ])

		# Minimum requirement for a valid site is the www folder.
		self.valid = False
		if os.path.exists(self.path['www']):
			self.valid = True

		if not os.access(self.basedir, os.W_OK | os.X_OK):
			self._critical('WARNING: User does not have write permissions in this directory!')

		self._loadlogging()
		self._loadconfig()
		self._loadtags()

	def _loadtags(self):
		self.tags = None

		if self.valid:
			if not os.path.exists(self.path['tags']):
				self._warning('Tags folder not present. Creating.')
				os.makedirs(self.path['tags'])

			self._info('Loading tag replacements...')
			self._info('Loading tags from: {}'.format(self.path['tags']))
			try:
				self.tags = HTMLReplacements([self.sppath['tags'], self.path['tags']])

				# Load additional standard tags:
				self.tags.add('sp:version', '<built-in>', __VERSION__)

				self._info('Tags loaded.')
			except Exception as e:
				self._critical('Unable to load tags. {}.'.format(type(e).__name__))

				if self._debugging:
					raise

	def _loadlogging(self):
		self.log = False

		if self.valid:
			if not os.path.exists(self.path['logs']):
				os.makedirs(self.path['logs'])

			self.log = True
			logging.basicConfig(filename=os.path.join(self.path['logs'], 'spm.log'),
					level=logging.INFO)

			self._info('Program started. ---------------------------------------------------------------')
			self._info('Log opened.')

			self._info('Running in: {}'.format(self.basedir))
			self._info('Logging to: {}'.format(self.path['logs']))
		else:
			print("Warning: No logs have been opened. You are alone.")

	def _loadconfig(self):
		self.config = {}

		if self.valid:
			if not os.path.exists(self.path['config']):
				os.makedirs(self.path['config'])
				self._warning('Config folder not present. Creating.')

			self._info('Loading config.')

			configpaths = [self.sppath['config'], self.path['config']]

			for p in configpaths:
				self._info('Loading config from: {}'.format(p))

				for f in os.listdir(p):
					path = os.path.join(p, f)

					if os.path.isfile(path):
						name, ext = os.path.splitext(f)

						if ext == '.conf':
							self._info('Loading config file: {}'.format(f))

							if ' ' in name:
								n = name.split(' ')[0]

								self._info('Config file with space in name: \'{}\'. Truncating to \'{}\''.format(
										name, n))

								name = n

							if name in self.config.keys():
								self._info('Config file context already present: \'{}\'! Merging.'.format(
									name))

								c = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
								c.read(path)

								for (k,v) in c.items():
									self.config[name][k] = v
							else:
								self.config[name] = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
								self.config[name].read(path)
						else:
							self._info('Non conf file in config folder: \'{}\'. Ignoring.'.format(f))
					else:
						self._info('Directory in config folder: \'{}\'. Ignoring.'.format(f))
			else:
				pass

		self._debugging = None
		if 'common' in self.config.keys():
			self._debugging = self.config['common'].get('debug', 'enable')

		if (self._debugging != None) and (self._debugging in ['yes', 'y', '1', 'on', 'enable', 'e', 't', 'true']):
			self._debugging = True
		else:
			self._debugging = False

	def _log(self, level, str):
		if self.log:
			logging.log(level, str)

	def _info(self, str, comm=''):
		if self.log:
			if comm != '':
				logging.info('{}: {}'.format(comm, str))
			else:
				logging.info(str)

		if comm != '':
			print(str)

	def _warning(self, str):
		if self.log:
			logging.warning(str)

	def _critical(self, str):
		if self.log:
			logging.critical(str)
		print('ERROR(CRITICAL):', str, file=sys.stderr)

	def _exception(self, str):
		if self.log:
			logging.exception(str)
		print(str, file=sys.stderr)

	def _debug(self, str):
		if self.log:
			logging.debug(str)

	def clean(self):
		if not self.valid:
			print('ERROR: Not in a valid site folder!')
		else:
			self._info('Removing all files...', 'clean')
			if (os.path.exists(self.path['cache'])):
				shutil.rmtree(self.path['cache'])
			self._info('Recreating folder...', 'clean')
			os.makedirs(self.path['cache'])
			self._info('Done.', 'clean')

	def init(self, SiteName):
		"""
		Creates a new site directory.
		The folder <SiteName> is created, and the directory structure is
		created allowing it to function as a site. The folder must NOT
		already exist.

		A valid site folder must contain at the minimum a folder called
		'www'. Other folders are optional, but will be created at runtime
		if they do not already exist.

		If the folder is detected to already be a valid site folder, then
		an error is printed and no further action is taken.
		"""
		print('Initializing new site directory.')

		path = os.path.join(self.basedir, SiteName)

		print('Path = {}'.format(path))

		if os.path.exists(path):
			if os.path.exists(os.path.join(path, self.dir['www'])):
				self._critical('Directory is already a valid site directory!')
			else:
				self._critical('Directory already exists!')

		skel = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'skel')
		print('Copying files from', skel)

		shutil.copytree(skel, path)

		print('Done! You new site is at', SiteName, '.')

	def gen(self, *files):
		"""
		Generates the site.
		`gen` is the most important command available, by default (when
		no files are specified) it will process the entire www folder contents
		and apply the transformations available to generate the output static
		pages in the cache directory.

		If files are given, then only they will be generated and copied. Files
		can also contain wildcards, or point to directories.
		"""
		self._info('Generating...', 'gen')

		if self._genlog not in self.tags.infof:
			self.tags.infof.append(self._genlog)

		if (len(files) == 0) or ('all' in files):
			file = None
			self._info('files: (All Files)', 'gen')
		else:
			self._info('files: {}'.format(', '.join(files)), 'gen')

		try:
			c = self.config['common'] if 'common' in self.config.keys() else None
			t = trans(self.dir, self.path, c, self.tags)

			try:
				t.run()

				self._info('Finished transfer. Log written to \'{}\'.'.format(t.log.fname), 'gen')
			except Exception as e:
				self._exception('Error during transfer. {}.'.format(type(e).__name__))
		except Exception as e:
			self._exception('Unable to initialise transfer. {}.'.format(type(e).__name__))

	def _genlog(self, str):
		self._info(str, 'gen')

	def server(self, cache_or_www=None, port=None):
		"""
		Starts a test server. *Requires Admin*
		Runs a simple http server, using either the cache or generating pages on
		the fly for the www copy.

		The settings are loaded from the config files, but can be overriden from the
		command line
		"""
		self._info('Setting up test server...', 'server')
		self._info('Set to listen on port {} using {}'.format(port, cache_or_www), 'server')

		if cache_or_www == None:
			try:
				cache_or_www = self.config['common']['server']['dir']
			except:
				cache_or_www = 'cache'

		if port == None:
			try:
				port = self.config['common']['server']['port']
			except:
				port = 80

		try:
			conf = None
			if 'server' in self.config.keys():
				conf = self.config['server']

			s = SPServer(conf, port, self.path[cache_or_www], __VERSION__, self._serverlog, self.path['logs'])
		except Exception as e:
			self._exception('Server stopped: {}'.format(type(e).__name__))

			if self._debugging:
				raise

	def _serverlog(self, str):
		self._info(str, 'server')

	def _dbg(self, what):
		if what == 'config':
			for (key,val) in self.config.items():
				print('[[{}]]'.format(key))

				for sect in val.sections():
					print('[{}]'.format(sect))

					for (k,v) in val[sect].items():
						print(k, '=', v)
		elif what == 'tags':
			print(self.tags)
		elif what == 'dir':
			print(list(sys.modules.keys()))
		else:
			print('What?')

if __name__ == '__main__':
	try:
		s = SPM(os.getcwd())
		c = CmdLine(s)

		args = sys.argv[1:]
		cmd = ''

		if len(args) > 0:
			cmd = args.pop(0)
		else:
			cmd = 'help'

		c.dispatch(cmd, args)

		del s
	except SPMError as e:
		print(e.args[1], file=sys.stderr)
	except CmdLineError as e:
		print(e.args[1], file=sys.stderr)