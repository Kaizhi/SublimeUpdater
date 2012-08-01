import sublime, sublime_plugin  
import urllib2
import shutil
import os
import threading 
import json
import sys
import formatter, htmllib
import subprocess
from urllib import quote


UPDATE_URL = "http://www.sublimetext.com/updates/2/stable/updatecheck" #url to check for latest st2 version
download_link = ""

class LinksParser(htmllib.HTMLParser):

    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.links = []

    def start_a(self, attrs):
        if len(attrs) > 0 :
            for attr in attrs :
                if attr[0] == "href":
                    if attr[1].find("rackcdn") != -1:
                        self.links.append(attr[1])

    def get_links(self):
        return self.links

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
        self.startInstaller()

    def getLatestVersion(self):
        data = urllib2.urlopen(UPDATE_URL).read()
        data = json.loads(data)
        return data['latest_version']

    def startInstaller(self):
        s = sublime.load_settings("Preferences.sublime-settings") #get the install path if any
        install_path = s.get("install_path")

        file_name = download_link[download_link.find("Sub"):]
        if len(install_path) == 0:
            run_params = [file_name, '/silent']
        else:
            run_params = [file_name, '/silent', '/dir=' + install_path]

        subprocess.call(run_params) #run the installer     

    def run(self):
        if int(self.getLatestVersion()) != int(sublime.version()):
            print ("currently on latest version")
        else:
            print ("new version available")
            if sublime.platform() == "windows":
                #download the latest installer

                f = urllib2.urlopen("http://www.sublimetext.com/2")
                format = formatter.NullFormatter()
                parser = LinksParser(format)
                html = f.read() 
                parser.feed(html) #get the list of latest installer urls
                parser.close()
                urls = parser.get_links()
                global download_link
                if sublime.arch() == "x32":
                    download_link = urls[1]

                elif sublime.arch() == "x64":
                    download_link = urls[3]

                download_link = quote(download_link, safe="%/:=&?~#+!$,;'@()*[]")
                thr = BackgroundDownloader(download_link)
                threads = []
                threads.append(thr)
                thr.start()
                self.handle_threads(threads)


            elif sublime.platform() == "linux":
                print "linux detected"
        
            elif sublime.platform() == "osx":
                print "mac detected"

