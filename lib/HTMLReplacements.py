
import os, imp, os.path, io
from TransParser import *

class HTMLReplacements:
	def __init__(self, tagDir='tags'):
		self.base = tagDir;
		self.repls = {}
		self.handlers = {}
		self.disallow = []

		self.ignore = ['__pycache__']

		self.loadRepls()

	def loadRepls(self):
		for d in os.listdir(self.base):
			if (d in self.ignore):
				pass
			elif os.path.isdir('{}/{}'.format(self.base, d)):
				for f in os.listdir('{}/{}/'.format(self.base, d)):
					if (f in self.ignore):
						pass
					elif os.path.isfile('{}/{}/{}'.format(self.base, d, f)):
						name, ext = os.path.splitext(f)

						if (ext == '.py'):
							try:
								mod = imp.load_source('{}.{}'.format(d, name), '{}/{}/{}'.format(self.base, d, f))

								self.repls['{}:{}'.format(d, name)] = (
									'{}/{}/{}'.format(self.base, d, f),
									mod)
							except AttributeError:
								pass
						else:
							self.repls['{}:{}'.format(d, name)] = ('{}/{}/{}'.format(self.base, d, f), None)
			else:
				name, ext = os.path.splitext(d)

				mod = imp.load_source('taghandler.{}'.format(name), '{}/{}'.format(self.base, d))

				if (name in self.handlers.keys()):
					self.handlers[name].append(mod)
				else:
					self.handlers[name] = [mod]

	def __getitem__(self, key):
		return self.get(key)

	def get(self, key, attrs=None):
		if (key not in self.repls.keys()):
			raise KeyError(key)

		file, ret = self.repls[key];

		if (file[-3:] == '.py'):
			return ret.handler(attrs)
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


