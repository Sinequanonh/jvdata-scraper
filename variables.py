# COLORS

import requests

red = "\033[31m";
green = "\033[32m";
magenta = "\033[35m";
cyan = "\033[36m";
blue = "\033[34m";
yellow = "\033[33m";
white = "\033[0m";

def singleRequest(url, s):
	try:
		r = s.request('GET', url, timeout=5)
		return r
	except:
		try:
			r = s.request('GET', url, timeout=5)
			return r
		except:
			print "Could not request this url: " + url
			return False
