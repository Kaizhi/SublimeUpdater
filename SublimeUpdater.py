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

class LinksParser(htmllib.HTMLParser): #helper class for scraping the site for download links
    
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
        
    def __init__(self, url, install_path, download_link):  
        self.url = url 
        self.result = None
        self.download_link = download_link
        self.install_path = install_path
        threading.Thread.__init__(self)  

    def startInstaller(self):
        file_name = self.download_link[self.download_link.find("Sub"):]

        if len(self.install_path) == 0:
            run_params = [sublime.packages_path() + "\\SublimeUpdater\\" + file_name, '/silent']
        else:
            run_params = [sublime.packages_path() + "\\SublimeUpdater\\" + file_name, '/silent', '/dir=' + self.install_path]

        subprocess.call(run_params) #run the installer       

    def run(self):  
        try:  
            file_name = self.url.split('/')[-1]
            u = urllib2.urlopen(self.url)
            f = open(sublime.packages_path() + "\\SublimeUpdater\\" + file_name, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)
            f.write(u.read())
            f.close()  
            self.result = True
            self.startInstaller()

            return
  
        except (urllib2.HTTPError) as (e):  
            err = '%s: HTTP error %s contacting URL' % (__name__, str(e.code))  
        except (urllib2.URLError) as (e):  
            err = '%s: URL error %s contacting URL' % (__name__, str(e.reason))  

        self.result = False  

class SublimeUpdaterCommand(sublime_plugin.ApplicationCommand):  

    def getLatestVersion(self):
        data = urllib2.urlopen(UPDATE_URL).read()
        data = json.loads(data)
        return data['latest_version']

    def run(self):
        if int(self.getLatestVersion()) == int(sublime.version()):
            print ("currently on latest version")
        else:
            print ("new version available")
            if sublime.platform() == "windows":
                #download the latest installer
                s = sublime.load_settings("Preferences.sublime-settings") #get the install path from preferences
                install_path = s.get("install_path", "")

                f = urllib2.urlopen("http://www.sublimetext.com/2")
                format = formatter.NullFormatter()
                parser = LinksParser(format)
                html = f.read() 
                parser.feed(html) #get the list of latest installer urls
                parser.close()
                urls = parser.get_links()
                if sublime.arch() == "x32":
                    download_link = urls[1]

                elif sublime.arch() == "x64":
                    download_link = urls[3]

                download_link = quote(download_link, safe="%/:=&?~#+!$,;'@()*[]")
                sublime.status_message('SublimeUpdater is downloading update')
                thr = BackgroundDownloader(download_link, install_path, download_link) #start the download thread
                threads = []
                threads.append(thr)
                thr.start()

            elif sublime.platform() == "linux":
                print "linux detected"
        
            elif sublime.platform() == "osx":
                print "mac detected"
