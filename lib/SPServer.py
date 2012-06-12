
import http.server, socketserver, os, sys
from ReplLog import Log

class SPRequestHandler(http.server.SimpleHTTPRequestHandler):
	mainlog = None
	serverlog = None
	logformat = '{} {:<15} {} {}'

	def writelog(self, code):
		self.serverlog(self.logformat.format(self.log_date_time_string(), self.address_string(),
				code, self.path))

	def log_request(self, code=None, size=None):
		self.writelog(code)

	def log_error(self, format, *args):
		print(self.path, format % args, file=sys.stderr)
		self.writelog(args[0])

	def log_message(self, format, *args):
		self.serverlog(format % args)

class SPServer:
	def __init__(self, conf, port, path, version, log, logpath):
		self.handler = SPRequestHandler

		self.serverlog = Log('server', logpath, False)
		self.handler.serverlog = self.serverlog.writes
		self.handler.mainlog = log

		port = int(port)
		os.chdir(path)

		if (conf != None) and ('mime' in conf.keys()):
			mime = conf['mime']

			log('Loading mime type config.')

			for (key, val) in mime.items():
				if key[0] != '.':
					key = '.{}'.format(key)

				self.handler.extensions_map[key] = val

		self.handler.server_version = 'SPM-Server/{}'.format(version)
		httpd = socketserver.TCPServer(("", port), self.handler)

		log('Server running on 127.0.0.1:{}'.format(port))

		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			self.serverlog.end()
			log('Server closed by user (KeyboardInterrupt)')