
import os, imp, os.path, io
from TransParser import *

class HTMLReplacements:
	def __init__(self, tagDir=['tags'], ignore = ['__pycache__'], logs=[], parser=None):
		p = tagDir;
		self.repls = {}
		self.handlers = {}
		self.disallow = []

		self.tagpaths = tagDir
		self.ignore = ignore
		self.infof = logs
		self.parser = parser

		self.loadRepls()

	def loadRepls(self):
		for p in self.tagpaths:
			for d in os.listdir(p):
				if (d in self.ignore):
					pass
				elif os.path.isdir(os.path.join(p, d)):
					for f in os.listdir(os.path.join(p, d)):
						if (f in self.ignore):
							pass
						elif os.path.isfile(os.path.join(p, d, f)):
							name, ext = os.path.splitext(f)

							if (ext == '.py'):
								try:
									mod = imp.load_source('{}.{}'.format(d, name), os.path.join(p, d, f))

									self.repls['{}:{}'.format(d, name)] = (
										os.path.join(p, d, f),
										mod)
								except AttributeError:
									raise
							else:
								print(d, name, sep=':')
								self.repls['{}:{}'.format(d, name)] = (os.path.join(p, d, f), None)
				else:
					name, ext = os.path.splitext(d)

					mod = imp.load_source('taghandler.{}'.format(name), os.path.join(p, d))

					if (name in self.handlers.keys()):
						self.handlers[name].append(mod)
					else:
						self.handlers[name] = [mod]

	def add(self, key, file, value):
		self.repls[key] = (file, value)

	def __getitem__(self, key):
		return self.get(key)

	def info(self, s):
		for f in self.infof:
			f(s)

	def get(self, key, attrs=None):
		if (key not in self.repls.keys()):
			self.info('Unrecognised tag: \'<{}>\' at {}. Ignoring.'.format(key,
					self.parser.getpos() if self.parser != None else '???'))
			return None

		file, ret = self.repls[key];

		if (file[-3:] == '.py'):
			try:
				return ret.handler(attrs)
			except Exception as e:
				self.info('Tag handler for \'<{}>\' threw exception \'{}\'.'.format(
						key, type(e).__name__))
				return '<!-- {} //-->'.format('{} -> ERROR: {}'.format(key, type(e).__name__))
		elif (ret == None):
			s = io.StringIO('')

			self.disallow.append(file) # Disallow nesting!

			p = TransParser(False, self, s)
			p.feedf(file)

			self.disallow.pop()

			ret = s.getvalue()
			self.repls[key] = (file, ret)

		return ret

	def transf(self, tag, attrs):
		if (tag in self.handlers.keys()):
			for h in self.handlers[tag]:
				try:
					return h.repl_handler(attrs)
				except AttributeError:
					try:
						h.handler(attrs)
					except AttributeError:
						pass

		return None


