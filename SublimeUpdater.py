import sublime, sublime_plugin  
import urllib2
import shutil
import urlparse
import os
import threading 
import json

DOWNLOAD_URL = "http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%202.0.1%20x64%20Setup.exe"
UPDATE_URL = "http://www.sublimetext.com/updates/2/stable/updatecheck" #url to check for latest st2 version



class ExampleCommand(sublime_plugin.ApplicationCommand):  

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

	def getLatestVersion():
		data = urllib2.urlopen(UPDATE_URL).read()
		data = json.loads(data)
		return data['latest_version']

	def run(self):
		if sublime.platform() == "windows":
			if getLatestVersion() == int(sublime.version()):
				print ("currently on latest version")
			else:
				print ("new version available")
				#download the latest installer
				thr = threading.Thread(target=download, args=(DOWNLOAD_URL,))
				thr.start()
	
		elif sublime.platform() == "linux":
			print "linux detected"
	
		elif sublime.platform() == "osx":
			print "mac detected"

