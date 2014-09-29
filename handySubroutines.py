import gzip;
import re;

def getFileHandle(filename):
	if (re.search('.gz$',filename) or re.search('.gzip',filename)):
		return gzip.open(filename)
	else:
		return open(filename) 



