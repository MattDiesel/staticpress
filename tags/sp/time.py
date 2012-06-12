
from datetime import datetime

def handler(attrs):
	if (attrs != None) and ('format' in attrs.keys()):
		return datetime.now().strftime(attrs['format'])
	else:
		return datetime.now().ctime()