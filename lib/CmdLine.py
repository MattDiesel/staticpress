
import sys, inspect

class CmdLineError(Exception):
	pass

class CmdLineBase:
	"""
	Base class for commands
	"""

	def help(self, command = None):
		"""
		Display help
		Displays all available commands or specific help for COMM if given.
		"""
		if command:
			# Display command-specific help
			try:
				func = getattr(self, command)
			except AttributeError as e:
				raise ICmdError(1, "No such command: '%s'. Type 'help [command]' for help." % (command))

			if not command.startswith('_') and callable(func):
				help = self._help_getspecifics(command)
				print(command, ': ', help[0], '\nUsage: ', help[2], '\n', sep='')

				for line in help[1].splitlines():
					print(' ', line)

				print('')
		else:
			# Display all available commands
			print('The following commands are available:\n')

			for cmd in dir(self):
				if not cmd.startswith('_') and callable(getattr(self, cmd)):
					help = self._help_getspecifics(cmd)
					print('  {:>10}: {}'.format(cmd, help[0]))

			print('\nType \'help <command>\' for more detailed help.')

	def _help_getspecifics(self, command):
		help_short = ''
		help_desc = ''
		help_usage = ''

		# Get short and full descriptions from the function's docstring.
		func = getattr(self, command)
		if func.__doc__:
			for line in func.__doc__.strip().splitlines():
				if line.lower().strip().startswith('usage:'):
					help_usage = line[8:].strip()
				elif not help_short:
					help_short = line.strip()
				else:
					help_desc += "%s\n" % (line.strip())

		# Get usage from the parameters
		if not help_usage:
			args = inspect.getargspec(func)

			parcnt_max = len(args.args) - 1
			parcnt_min = len(args.args) - 1 - len(args.defaults or '')
			help_usage = command
			for i in range(1, len(args.args)):
				if i <= parcnt_min:
					help_usage += ' <{}>'.format(args.args[i])
				else:
					help_usage += ' [{}]'.format(args.args[i])

			if args.varargs:
				help_usage += ' [{0} ...]'.format(args.varargs)

		return([help_short.strip(), help_desc.strip(), help_usage.strip()])

class CmdLine:
	def __init__(self, cl):
		self.instclass = cl

	def dispatch(self, cmd, params):
		try:
			func = getattr(self.instclass, cmd)
			getattr(func, '__call__') # Test callability
		except AttributeError as e:
			raise CmdLineError(1, "No such command: '%s'. Type 'help [command]' for help." % (cmd))

		args = inspect.getargspec(func)

		parcnt_given = len(params)
		parcnt_max = len(args.args) - 1
		parcnt_min = len(args.args) - 1 - len(args.defaults or '')

		if parcnt_given < parcnt_min:
			raise CmdLineError(2, 'Not enough parameters given')
		elif not args.varargs and parcnt_given > parcnt_max:
			raise CmdLineError(3, 'Too many parameters given')

		return(func(*params))