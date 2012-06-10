
import http.server, socketserver, os

class SPRequestHandler(http.server.SimpleHTTPRequestHandler):
	pass

class SPServer:
	def __init__(self, conf, port, path, version, log):
		self.handler = SPRequestHandler

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
		httpd.serve_forever()