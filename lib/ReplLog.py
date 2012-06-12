
import os.path, sys


class Log:
	def __init__(self, name=None, dir='logs', repl=True):
		self.dir = dir

		if name == None:
			p,self.command = os.path.split(sys.argv[0])
		else:
			self.command = '{}.py'.format(name)
		self.command,ext = os.path.splitext(self.command)
		self.index = 0

		while (os.path.exists('{}\\{}{}.log'.format(self.dir, self.command, self.index))):
			self.index += 1

		self.fname = '{}\\{}{}.log'.format(self.dir, self.command, self.index)

		self.fd = open(self.fname, 'wt', encoding='utf-8')

		self.usecounters = repl

		if repl:
			self.counters = {
				'*:*': 0,
			}

	def write(self, file, action, result):
		if self.usecounters:
			key = '{}:{}'.format(action, result)
			if (key not in self.counters):
				self.counters[key] = 1
			else:
				self.counters[key] += 1

			key = '*:{}'.format(result)
			if (key not in self.counters):
				self.counters[key] = 1
			else:
				self.counters[key] += 1

			key = '{}:*'.format(action)
			if (key not in self.counters):
				self.counters[key] = 1
			else:
				self.counters[key] += 1

			self.counters['*:*'] += 1

		print(file, action, result, sep=',', file=self.fd)
		self.fd.flush()

	def writes(self, s):
		print(s, file=self.fd)
		self.fd.flush()

	def printStats(self):
		if self.usecounters:
			print('-- SUMMARY ---------', file=self.fd)

			for (key, val) in self.counters.items():
				print(key, val, sep=" = ", file=self.fd)

	def end(self):
		self.printStats()
		self.fd.close()