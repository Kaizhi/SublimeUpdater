import sublime, sublime_plugin  
import urllib2
import shutil
import urlparse
import os
import threading 


def download(url, fileType="None"):
	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)

	f.close()


class ExampleCommand(sublime_plugin.ApplicationCommand):  
	def run(self):
		thr = threading.Thread(target=download, args=('http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%202.0.1%20x64%20Setup.exe',))
		thr.start() # will run "foo"

