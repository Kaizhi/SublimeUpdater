import sublime, sublime_plugin  
import urllib2
import shutil
import urlparse
import os
import threading 
import json
import sys

DOWNLOAD_URL = "http://c758482.r82.cf2.rackcdn.com/Sublime%20Text%202.0.1%20x64%20Setup.exe"
UPDATE_URL = "http://www.sublimetext.com/updates/2/stable/updatecheck" #url to check for latest st2 version
#http://unattended.sourceforge.net/InnoSetup_Switches_ExitCodes.html

class BackgroundDownloader(threading.Thread):  
        
    def __init__(self, url):  
        self.url = url 
        self.result = None
        threading.Thread.__init__(self)  

    def run(self):  
        try:  
            file_name = self.url.split('/')[-1]
            u = urllib2.urlopen(self.url)
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
            self.result = True
            return
  
        except (urllib2.HTTPError) as (e):  
            err = '%s: HTTP error %s contacting URL' % (__name__, str(e.code))  
        except (urllib2.URLError) as (e):  
            err = '%s: URL error %s contacting URL' % (__name__, str(e.reason))  

        self.result = False  

class SublimeUpdaterCommand(sublime_plugin.ApplicationCommand):  
    def handle_threads(self,threads):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue

        threads = next_threads

        if len(threads):
            sublime.status_message('SublimeUpdater is downloading update')

            sublime.set_timeout(lambda: self.handle_threads(threads), 50)
            return

        sublime.status_message('SublimeUpdater download succeeded, installing... ')

    def getLatestVersion(self):
        data = urllib2.urlopen(UPDATE_URL).read()
        data = json.loads(data)
        return data['latest_version']

    def run(self):
        if sublime.platform() == "windows":
            if int(self.getLatestVersion()) == int(sublime.version()):
                print ("currently on latest version")
            else:
                print ("new version available")
                #download the latest installer
                thr = BackgroundDownloader(DOWNLOAD_URL)
                threads = []
                threads.append(thr)
                thr.start()
                self.handle_threads(threads)
    
        elif sublime.platform() == "linux":
            print "linux detected"
    
        elif sublime.platform() == "osx":
            print "mac detected"

