
import os, os.path, fnmatch

def traverse(dir='www', ignore=[], match=['*.html', '*.py', 'redirect.*']):
	for d in os.listdir(dir):
		path = '{}/{}'.format(dir, d)

		if ((d in ignore) or (d[0:1] == '.')):
			pass
		elif (os.path.isdir(path)):
			traverse(path, ignore)
		else:
			name, ext = os.path.splitext(d)

			for m in match:
				if (fnmatch.fnmatch(d, m)):
					print(path)

traverse()