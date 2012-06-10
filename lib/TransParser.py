
from html.parser import HTMLParser

class TransParser(HTMLParser):
	def __init__(self, strict = False, reps = None, outs = None, sc = True):
		self.rep = reps
		self.outStream = outs
		self.stripComment = sc
		self.rep.parser = self

		HTMLParser.__init__(self, strict)

	def feedf(self, file):
		f = open(file, "rt", encoding="utf-8")
		self.feed(f.read(None))
		f.close()

	def attrs(self, attr):
		if (len(attr) > 0):
			return ' ' + ' '.join(['{}="{}"'.format(a, v) for (a, v) in attr.items()])
		else:
			return ''

	def out(self, s):
		print(s, sep='', end='', file=self.outStream)

	def handle_startendtag(self, tag, attrs):
		attrs = dict(attrs)

		r = None

		if (self.rep != None):
			r = self.rep.transf(tag, attrs)

		if ((r == None) and self.rep and (':' in tag)):
			r = self.rep[tag]

		if (r != None):
			self.out(r)
		else:
			self.out('<{}{} />'.format(tag, self.attrs(attrs)))

	def handle_pi(self, proc):
		exec(proc.strip('?').strip())

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)

		r = None

		if (self.rep != None):
			r = self.rep.transf(tag, attrs)

		if ((r == None) and self.rep and (':' in tag)):
			r = self.rep[tag]

		if (r != None):
			self.out(r)
		else:
			self.out("<{}{}>".format(tag, self.attrs(attrs)))

	def handle_endtag(self, tag):
		self.out("</{}>".format(tag))

	def handle_data(self, data):
		self.out(data)

	def handle_decl(self, data):
		self.out("<!{}>".format(data))

	def handle_comment(self, data):
		if (not self.stripComment):
			self.out("<!-- {} //-->".format(data.strip('-!<>/ ')))

	def handle_entityref(self, name):
		self.out('&{};'.format(name))

	def handle_charref(self, name):
		self.out('&{};'.format(name))