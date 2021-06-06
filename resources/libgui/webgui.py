'''
    Copyright (C) 2014-2016 ddurdle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''



from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

from SocketServer import ThreadingMixIn
import threading
import re
import urllib, urllib2
import sys
import socket
import string
import random
import os

import constants
from resources.lib import engine
from resources.libgui import xbmcplugin
from resources.libgui import settingsdbm
from resources.libgui import xbmc
from resources.libgui import xbmcaddon


if constants.CONST.DEBUG:

    #debugging
    import hashlib

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ThreadedWebGUIServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class WebGUIServer(ThreadingMixIn,HTTPServer):

    def __init__(self, *args, **kw):
        HTTPServer.__init__(self, *args, **kw)
        self.ready = True
        import constants
        #self.addon = constants.addon
        self.addon = None#xbmcaddon.xbmcaddon(dbm)
        self.hide = False
        self.keyvalue = False
        self.saltfile = None
        self.saltpassword = None
        self.cryptoSalt = None
        self.cryptoPassword = None
        self.embyFilterUsers = False
        self.embyLog = None
        self.embyLogPtr = 0
        self.embyUserList = {}
        self.logins = {}
        self.embyUserList['127.0.0.1'] = True
        self.embyUserList[str(self.get_ip_address())] = True
        self.fileIDList = None
        self.MD5List = None
        self.namesList = None

    # set port
    def setPort(self, port):
        self.port = port

    # set DBM
    def setDBM(self, dbm=None):

        if dbm is not None:
            self.dbm = settingsdbm.settingsdbm(dbm)
        else:
            self.dbm.reset()
        self.addon = xbmcaddon.xbmcaddon(dbm=self.dbm)
        #constants.addon = self.addon

        # login password?
        try:
            self.username = self.dbm.getSetting('username')
            self.password = self.dbm.getSetting('password')
        except:
            self.username = None
            self.password = None

        try:
            if self.dbm.getSetting('hide') == 'true' and self.password != None:
                self.hide = True
            else:
                self.hide = False
            if self.dbm.getSetting('keyvalue') == 'true':
                self.keyvalue = True
            else:
                self.keyValue = False
        except: pass



        try:
            plexNames = self.dbm.getSetting('plex_names')

            if plexNames != None:
                xbmc.log('plexNames ' + str(plexNames))
                self.namesList = {}

                xbmc.log('FILE = ' + str(plexNames))
                f = open(plexNames, "r")
                for line in f:
                    line = line.rstrip()
                    entry = line.split(",")
                    name = entry[0]
                    hash = entry[1]
                    self.namesList[name] = hash
                f.close()

        except: pass

        try:
            if self.dbm.getSetting('emby_user') == 'true':
                self.embyLog = self.dbm.getSetting('emby_log')
                self.embyFilterUsers = True
                embyIP = self.dbm.getSetting('emby_ip')
                for IP in embyIP.split(","):
                    self.embyUserList[IP] = True

        except: pass

        try:
            from resources.lib import encryption

            try:
                self.saltfile = self.dbm.getSetting('saltfile', default='saltfile')
                self.saltpassword = self.dbm.getSetting('saltpassword', default='saltpassword')
            except:
                self.saltfile = 'saltfile'
                self.saltpassword = 'saltpassword'
                xbmc.log("No saltfile set, using file \'" + self.saltfile + "\' instead.")

            self.encrypt = encryption.encryption(self.saltfile,self.saltpassword)
        except:
            self.encrypt = None
            #print "ENCRYPT = FALSE\n\n"


        try:
            self.cryptoSalt = self.dbm.getSetting('crypto_salt')
            self.cryptoPassword = self.dbm.getSetting('crypto_password')
        except: pass

        xbmc.openLog(self.dbm.getSetting('logfile', None), debug=self.dbm.getBoolSetting('debug', False))


        self.loadHash(False)

    # hash file db
    def loadHash(self,reload):
        if reload:
            self.fileIDList = None
        if self.fileIDList is None:#try:
            hashfiles = self.dbm.getSetting('md5files')

            if hashfiles != None:
                xbmc.log('hashfiles ' + str(hashfiles))
                self.fileIDList = {}
                self.MD5List = {}

                count = 0
                for file in hashfiles.split(","):
                    xbmc.log('FILE = ' + str(file))
                    f = open(file, "r")
                    if count == 0:
                        for line in f:
                                line = line.rstrip()
                                entry = line.split(",")
                                id = entry[0]
                                hash = entry[1]
                                self.fileIDList[id] = hash
                        count = count + 1
                    else:
                        for line in f:
                                line = line.rstrip()

                                entry = line.split(",")
                                id = entry[1]
                                hash = entry[0]
                                ids = entry[1].split("|")

                                self.MD5List[hash] = ids
                    f.close()
                    xbmc.log('loop')



    def file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


    def readLog(self,fname):
        xbmc.log('opening emby log...')
        for filename in fname.split(","):
            if os.path.isfile(filename):
                with open(filename) as f:
                    xbmc.log('searching emby log...')
                    line = f.readline()
                    count = 0
                    while line:
                        results = re.search(r' to (\S+)\. .*?/Users/\w{32}/', str(line))
                        if results:
                            IP = str(results.group(1))
                            self.embyUserList[IP] = True
                            #print "found IP = " + IP + "\n"
                            count = count + 1

                        line = f.readline()


    def whitelistIPs():
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def checkIP(self,IP):
        try:
            return self.embyUserList[IP]
        except:
            xbmc.log('IP not found ' + IP)
        return False

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

class webGUI(BaseHTTPRequestHandler):



    def __init__(self, *args):
        self.override = False

        BaseHTTPRequestHandler.__init__(self, *args)


    def log_message(self, format, *args):
        message =  "%s - %s - [%s] %s\n" % (self.address_string(), self.client_address[0],self.log_date_time_string(),format%args)
        print >> sys.stderr, message
        xbmc.log(message)

    def log_error(self, format, *args):
        message =  "%s - %s - [%s] %s\n" % (self.address_string(), self.client_address[0],self.log_date_time_string(),format%args)
        print >> sys.stderr, message
        xbmc.log(message)

    #Handler for the GET requests
    def do_POST(self):

        IP =  self.client_address[0]

        if self.server.embyFilterUsers:

            if not self.server.checkIP(IP):
                self.server.readLog(self.server.embyLog)
                if not self.server.checkIP(IP):
                    self.send_response(403)
                    self.end_headers()
                    return
                else:
                    xbmc.log('accepted whitelisted IP ' + IP)

            else:
                xbmc.log('accepted whitelisted IP ' + IP)


        #decryptkeyvalue = self.path
        #if re.search(r'kv\=', str(self.path)):
        #    from resources.lib import encryption

        #    results = re.search(r'kv\=(.*)$', str(self.path))
        #    if results:
        #        keyvalue = str(results.group(1))
        #        decryptkeyvalue = '/' + self.server.encrypt.decryptString(keyvalue).strip()
        #        print decryptkeyvalue +"."
        decryptkeyvalue = self.path
        if re.search(r'kv\=', str(self.path)):
            from resources.lib import encryption

            results = re.search(r'kv\=([^\&]+)', str(self.path))
            if results:
                keyvalue = str(results.group(1))
                decryptkeyvalue = '/' + self.server.encrypt.decryptString(keyvalue).strip()
                results = re.search(r'kv\=[^\&]+(\&.*)$', str(self.path))
                if results:
                    extras = str(results.group(1))
                    decryptkeyvalue = decryptkeyvalue + extras
                print decryptkeyvalue +"."


        # debug - print headers in log
        headers = str(self.headers)
        xbmc.log(self.requestline)
        xbmc.log(headers)

        host = re.search(r'Host: (\S+)', str(headers))
        if host is not None:
            host = str(host.group(1))


        isLoggedIn = self.cookieLogin(self.headers)
        if IP == '127.0.0.1':
            isLoggedIn = True


        #require authentication for all further requests
        if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                post_data = self.rfile.read(content_length) # <--- Gets the data itself

                username = ''
                password = ''
                for r in re.finditer('username\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    username = r.group(1)
                for r in re.finditer('password\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    password = r.group(1)
                if self.server.username == username and self.server.password == password:
                    loginSession =  id_generator(size=10)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Set-Cookie', 'login='+str(loginSession))
                    self.server.logins[loginSession] = 1
                    mediaEngine = engine.contentengine()
                    mediaEngine.run(self, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write("Wrong username/password")

                    self.wfile.write('<html><form action="/list" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
                return



        # passed a kill signal?
        if decryptkeyvalue == '/kill':
            if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                post_data = self.rfile.read(content_length) # <--- Gets the data itself
                #print post_data

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                username = ''
                password = ''
                for r in re.finditer('username\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    username = r.group(1)
                for r in re.finditer('password\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    password = r.group(1)
                if self.server.username == username and self.server.password == password:
                    self.wfile.write("Stopping server...")
                    self.server.ready = False
                    print "Stopping server...\n"
                else:
                    self.wfile.write("Wrong username/password")


            else:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write("Stopping server...")
                self.server.ready = False
                print "Stopping server...\n"
            return


        # redirect url to output
        elif re.search(r'/default.py\?mode\=enroll\&default\=false', str(decryptkeyvalue),re.IGNORECASE):
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')

            self.end_headers()

            for r in re.finditer('client_id\=([^\&]+)\&\client_secret\=([^\&]+)' ,
                     post_data, re.DOTALL):
                client_id = r.group(1)
                client_secret = r.group(2)


                self.wfile.write('<html><body>Two steps away.<br/><br/>  1) Visit this site and then paste the application code in the below form: <a href="https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/drive&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&client_id='+str(client_id)+'" target="new">Google Authentication</a><br /><br />2) Return back to this tab and provide a nickname and the application code provided in step 1. <form action="/default.py?mode=enroll" method="post">Nickname for account:<br /><input type="text" name="account"><br />Code (copy and paste from step 1):<br /><input type="text" name="code"><br /><form action="default.py?mode=enroll" method="post">Client ID:<br /><input type="text" name="client_id" value="'+str(client_id)+'"><br />Client Secret:<br /><input type="text" name="client_secret" value="'+str(client_secret)+'"><br /><br /> <input type="submit" value="Submit"></form></body></html>')

        elif re.search(r'/save_settings', str(decryptkeyvalue),re.IGNORECASE):
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')

            self.end_headers()
            xbmc.log(post_data)
            isPassthrough = False
            for r in re.finditer('\&?([^\=]+)\=([^\&]*)' ,
                     post_data, re.DOTALL):
                key = r.group(1)
                value = r.group(2)
                value = value.replace("%2F",'/')
                value = value.replace("%3F",'?')
                value = value.replace("%26",'&')
                value = value.replace("%5C",'\\')
                value = value.replace("%24",'$')
                value = value.replace("%3A",':')
                key = key.replace('passwrd','password')

                if str(key) == 'passthrough' and str(value) == 'true':
                    isPassthrough = True

                if str(key) == 'never_stream' and isPassthrough:
                    value = 'true'



                xbmc.log("saving key, value " + str(key) +str(value))
                self.server.dbm.setSetting(key,value)

            self.wfile.write('<html><body>Changes saved.  You must restart the service or click <a href="/reload">reload</a> to make the changes take in effect.</body></html>')

        elif re.search(r'/settings', str(decryptkeyvalue),re.IGNORECASE):

            if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                post_data = self.rfile.read(content_length) # <--- Gets the data itself
                #print post_data

                username = ''
                password = ''
                for r in re.finditer('username\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    username = r.group(1)
                for r in re.finditer('password\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    password = r.group(1)
                xbmc.log("username " + username + " password " + self.server.username)
                if not (self.server.username == username and self.server.password == password):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')

                    self.end_headers()
                    self.wfile.write("Wrong username/password")
                    return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')

            self.end_headers()

            self.displaySettings(host=host)


        # redirect url to output
        elif  re.search(r'/default.py\?mode\=enroll', str(decryptkeyvalue),re.IGNORECASE):
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            for r in re.finditer('account\=([^\&]+)\&code=([^\&]+)\&\client_id\=([^\&]+)\&\client_secret\=([^\&]+)' ,
                     post_data, re.DOTALL):
                account = r.group(1)
                client_id = r.group(3)
                client_secret = r.group(4)
                code = r.group(2)
                code = code.replace('%2F','/')


                count = 1
                loop = True
                while loop:
                    instanceName = constants.PLUGIN_NAME +str(count)
                    try:
                        username = self.server.addon.getSetting(instanceName+'_username')
                    except:
                        username = None

                    if username == account or username is None:
                        self.server.addon.setSetting(instanceName + '_type', str(3))
                        self.server.addon.setSetting(instanceName + '_code', str(code))
                        self.server.addon.setSetting(instanceName + '_client_id', str(client_id))
                        self.server.addon.setSetting(instanceName + '_client_secret', str(client_secret))
                        self.server.addon.setSetting(instanceName + '_username', str(account))
                        loop = False

                    count = count + 1

                results = re.search(r'\?(.*)$', str(decryptkeyvalue))
                if results:
                    query = str(results.group(1))


                url = 'https://accounts.google.com/o/oauth2/token'
                header = { 'User-Agent' : self.server.addon.getSetting('user_agent')  , 'Content-Type': 'application/x-www-form-urlencoded'}

                req = urllib2.Request(url, 'code='+str(code)+'&client_id='+str(client_id)+'&client_secret='+str(client_secret)+'&redirect_uri=urn:ietf:wg:oauth:2.0:oob&grant_type=authorization_code', header)


                # try login
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                    if e.code == 403:
                        #login issue
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(str(e))
                        return
                    else:
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(str(e))
                    return


                response_data = response.read()
                response.close()

                # retrieve authorization token
                for r in re.finditer('\"access_token\"\s?\:\s?\"([^\"]+)\".+?' +
                                 '\"refresh_token\"\s?\:\s?\"([^\"]+)\".+?' ,
                                 response_data, re.DOTALL):
                    accessToken,refreshToken = r.groups()
                    self.server.addon.setSetting(instanceName + '_auth_access_token', str(accessToken))
                    self.server.addon.setSetting(instanceName + '_auth_refresh_token', str(refreshToken))

                    mediaEngine = engine.contentengine()
                    mediaEngine.run(self,  DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)


                for r in re.finditer('\"error_description\"\s?\:\s?\"([^\"]+)\"',
                                 response_data, re.DOTALL):
                    errorMessage = r.group(1)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(errorMessage)

                return


        elif decryptkeyvalue == '/list' or decryptkeyvalue == '/':

            if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                post_data = self.rfile.read(content_length) # <--- Gets the data itself

                username = ''
                password = ''
                for r in re.finditer('username\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    username = r.group(1)
                for r in re.finditer('password\=([^\&]+)' ,
                         post_data, re.DOTALL):
                    password = r.group(1)
                if self.server.username == username and self.server.password == password:
                    loginSession =  id_generator(size=10)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Set-Cookie', 'login='+str(loginSession))
                    self.server.logins[loginSession] = 1
                    mediaEngine = engine.contentengine()
                    mediaEngine.run(self, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write("Wrong username/password")

            else:
                mediaEngine = engine.contentengine()
                mediaEngine.run(self, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)


    def do_HEAD(self):

        # debug - print headers in log
        headers = str(self.headers)
        xbmc.log(self.requestline)
        xbmc.log(headers)

        # passed a kill signal?
        if self.path == '/kill':
#            self.server.ready = False
            return



    #Handler for the GET requests
    def do_GET(self):


        if self.path == '/favicon.ico':
            return

        IP =  self.client_address[0]


        decryptkeyvalue = self.path
        if re.search(r'kv\=', str(self.path)):
            from resources.lib import encryption

            results = re.search(r'kv\=([^\&]+)', str(self.path))
            if results:
                keyvalue = str(results.group(1))
                decryptkeyvalue = '/' + self.server.encrypt.decryptString(keyvalue).strip()
                results = re.search(r'kv\=[^\&]+(\&.*)$', str(self.path))
                if results:
                    extras = str(results.group(1))
                    decryptkeyvalue = decryptkeyvalue + extras
                print decryptkeyvalue +"."



        # debug - print headers in log
        headers = str(self.headers)
        xbmc.log(self.requestline)
        xbmc.log(headers)


        if self.server.embyFilterUsers:

            IP = re.search(r'X-Real-IP: (\S+)', str(headers))
            if IP is not None:
                IP = str(IP.group(1))
            else:
                IP =  self.client_address[0]

            if not self.server.checkIP(IP):
                self.server.readLog(self.server.embyLog)
                if not self.server.checkIP(IP):
                    self.send_response(403)
                    self.end_headers()
                    return
                else:
                    xbmc.log('accepted whitelisted IP ' + IP)

            else:
                xbmc.log('accepted whitelisted IP ' + IP)


        host = re.search(r'Host: (\S+)', str(headers))
        if host is not None:
            host = str(host.group(1))


        isLoggedIn = self.cookieLogin(self.headers)
        if IP == '127.0.0.1':
            isLoggedIn = True

        start = ''
        end = ''
        startOffset = 0
        for r in re.finditer('Range\:\s+bytes\=(\d+)\-' ,
                     headers, re.DOTALL):
          start = int(r.group(1))
          break
        for r in re.finditer('Range\:\s+bytes\=\d+\-(\d+)' ,
                     headers, re.DOTALL):
          end = int(r.group(1))
          break

        # method to force direct play via Google Drive
        if re.search(r'/stream/', str(decryptkeyvalue),re.IGNORECASE):

                results = re.search(r'/stream/([^\/]+)/([^\/]+)/([^\/]+)/([^\/]+)/', str(decryptkeyvalue))
                xbmc.log("STREAM  = " +str(decryptkeyvalue))
                if not results:
                    results = re.search(r'/stream/([^\/]+)/([^\/]+)/([^\/]+)/', str(decryptkeyvalue))
                    xbmc.log("STREAM (deprecated) = " +str(decryptkeyvalue))

                if results:
                    API = str(results.group(1))
                    fileID = str(results.group(2))
                    port = str(results.group(3))
                    try:
                       host = str(results.group(4))
                    except:
                       host= '127.0.0.1'

                    #old method API call
                    #req = urllib2.Request('http://127.0.0.1:'+str(port)+'/emby/Items/'+ str(fileID) + '/File?api_key=' +str(API),None)
                    URL = 'http://127.0.0.1:'+str(port)+'/emby/Items/'+ str(fileID) + '/PlaybackInfo?api_key=' +str(API)
                    req = urllib2.Request(URL,None)


                    # try login
                    try:
                        response = urllib2.urlopen(req)
                    except urllib2.URLError, e:
                        if e.code == 403:
                            #login issue
                            self.send_response(200)
                            self.send_header('Content-Type', 'text/html')
                            self.end_headers()
                            self.wfile.write(str(e))
                        else:
                            xbmc.log("STREAM FAIL = " +str(URL) +  '  -- '+ str(decryptkeyvalue))

                            self.send_response(307)
                            self.send_header('Location', 'http://'+str(host)+':'+str(port)+'/emby/Videos/'+ str(fileID) + '/stream?Static=true&api_key=' +str(API))
                            self.end_headers()

                        return

                    response_data = response.read()
                    response.close()


                    results = re.search(r'"Path":"([^\"]+)"', str(response_data), re.IGNORECASE)
                    xbmc.log("OVERRIDE = " +str(response_data))
                    if results:

                        filenameWithPath = str(results.group(1))
                        xbmc.log("filenameWithPath = " +str(filenameWithPath))
                        if re.search('\.strm', str(filenameWithPath), re.IGNORECASE):
                            try:
                                f=open(filenameWithPath, "r")
                                if f.mode == 'r':
                                    URL =f.readline()
                                    URL.rstrip("\n")
                                    URL.rstrip("\r")
                                    f.close()
                                    self.send_response(307)
                                    self.send_header('Location', URL)
                                    self.end_headers()
                            except:
                                pass
                        elif re.search('htt', str(filenameWithPath), re.IGNORECASE):
                            self.send_response(307)
                            self.send_header('Location', str(filenameWithPath))
                            self.end_headers()
                            return



                    xbmc.log("STREAM catchall = "  +str(URL) +  '  -- '+ str(decryptkeyvalue))

                    self.send_response(307)
                    self.send_header('Location', 'http://'+str(host)+':'+str(port)+'/emby/Videos/'+ str(fileID) + '/stream?Static=true&api_key=' +str(API))
                    self.end_headers()
                    return

        # Plex name to hash
        elif re.search(r'/TEST\?file\=', str(decryptkeyvalue),re.IGNORECASE):

                results = re.search(r'/TEST\?file\=([^\&]+)(\&?.*?)$', str(decryptkeyvalue))
                xbmc.log("TEST = " +str(decryptkeyvalue))

                if results:
                    filename = str(results.group(1))
                    parameters = str(results.group(2))
                    filename = filename.replace("%20",' ')

                    xbmc.log("filename = " +str(self.server.namesList[filename]))
                    hash = self.server.namesList[filename]
                    filenames = self.server.MD5List[hash]

                    query = 'mode=video&instance=gdrive1&filename='+str(filenames[0])+'&title=' + str(filename) + str(parameters)
                    #self.send_response(307)
                    #self.send_header('Location', 'http://127.0.0.1:9988/default.py?' + query)
                    #self.end_headers()
                    quality = str(self.cookieQuality(headers))
                    if quality != '':
                        query = query + quality
                        self.override = True

                    if '&override=true' in query:
                        self.override = True


                    #xbmc.log("query = " +str(query))
                    mediaEngine = engine.contentengine()
                    mediaEngine.run(self,query, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
                    return
        elif  re.search(r'/quality=SD', str(decryptkeyvalue),re.IGNORECASE) or re.search(r'/quality=720p', str(decryptkeyvalue),re.IGNORECASE) or re.search(r'/quality=1080p', str(decryptkeyvalue),re.IGNORECASE) or re.search(r'/quality=unset', str(decryptkeyvalue),re.IGNORECASE):
            self.send_response(200)
            if re.search(r'/quality=SD', str(decryptkeyvalue),re.IGNORECASE):
                self.send_header('Set-Cookie', 'quality=2')
            elif re.search(r'/quality=720p', str(decryptkeyvalue),re.IGNORECASE):
                self.send_header('Set-Cookie', 'quality=1')
            elif re.search(r'/quality=1080p', str(decryptkeyvalue),re.IGNORECASE):
                self.send_header('Set-Cookie', 'quality=0')
            elif re.search(r'/quality=unset', str(decryptkeyvalue),re.IGNORECASE):
                self.send_header('Set-Cookie', 'quality=')

            self.send_header('Content-type','video/mp4')
            f =open('./resources/videos/transcode.mp4', 'rb')
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.close()
            self.send_header('Content-Length',str(size))
            self.send_header('Content-Range','bytes '+str(start)+'-' + str(end) + '/' +  str(size))
            xbmc.log('Content-Range'+' bytes '+str(start)+'-' + str(end) + '/' +  str(size))

            self.end_headers()
            #with open('./resources/videos/transcode.mp4', 'rb') as f:
            f =open('./resources/videos/transcode.mp4', 'rb')
            f.seek(start)
            content = f.read()
            f.close()
            self.wfile.write(content)
            return


            # redirect url to output
        elif re.search(r'/play', str(decryptkeyvalue)):
#            self.send_response(200)
#            self.end_headers()
            count = 0
            isEncrypted = False
            results = re.search(r'/play\?count\=(\d+)\&encrypted\=true$', str(decryptkeyvalue),re.IGNORECASE)
            #encrypted stream
            if results:
                count = int(results.group(1))
                isEncrypted = True
            #not encrypted stream
            else:
                results = re.search(r'/play\?count\=(\d+)$', str(decryptkeyvalue),re.IGNORECASE)
                if results:
                    count = int(results.group(1))

            #self.send_response(200)
            #self.end_headers()
            #xbmcplugin.assignOutputBuffer(self.wfile)
            #cookies = self.headers['Cookie']
            cookie = xbmcplugin.playbackBuffer.playback[count]['cookie']
            url = xbmcplugin.playbackBuffer.playback[count]['url']
            auth = xbmcplugin.playbackBuffer.playback[count]['auth']
            auth = auth.replace("+",' ')


            if url == 'BROKEN':
                xbmc.log("send transcode broken ERROR")
                self.send_response(200)
                self.send_header('Content-type','video/mp4')
                f =open('./resources/videos/transcode.mp4', 'rb')
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.close()
                self.send_header('Content-Length',str(size))
                self.send_header('Content-Range','bytes '+str(start)+'-' + str(end) + '/' +  str(size))
                xbmc.log('Content-Range'+' bytes '+str(start)+'-' + str(end) + '/' +  str(size))

                self.end_headers()
                #with open('./resources/videos/transcode.mp4', 'rb') as f:
                f =open('./resources/videos/transcode.mp4', 'rb')
                f.seek(start)
                content = f.read()
                f.close()
                self.wfile.write(content)
                return


            length=0
            try:
                length = xbmcplugin.playbackBuffer.playback[count]['length']
            except:
                length = 0
                start= ''

            endOffset = 0
            startOffset = 0
            specialEnd = 0

            if isEncrypted:

                from resources.lib import  encryption
                decrypt = encryption.encryption(self.server.cryptoSalt,self.server.cryptoPassword)

                try:
                    if xbmcplugin.playbackBuffer.playback[count]['length'] == -1:
                        return
                except:
                    #for encrypted streams
                    # need to fetch the last 16 bytes to calculate unpadded size
                    if isEncrypted:
                        req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth})
                        try:
                            response = urllib2.urlopen(req)
                        except urllib2.URLError, e:
                            if e.code == 403 or e.code == 401:
                                xbmc.log("STILL ERROR " +url +str(e.code))
                                return
                            else:
                                return
                        response.close()
                        xbmcplugin.playbackBuffer.playback[count]['length'] =  response.info().getheader('Content-Length')

                        req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth, 'Range': 'bytes='+str(int(xbmcplugin.playbackBuffer.playback[count]['length']) - 16 - 8 )+'-'})
                        try:
                            response = urllib2.urlopen(req)
                        except urllib2.URLError, e:
                            if e.code == 403 or e.code == 401:
                                xbmc.log("STILL ERROR " +url +str(e.code))
                                return
                            else:
                                return
                        CHUNK = 16 * 1024

                        #originalSize = decrypt.decryptCalculateSizing(response)
                        #print "size " + response.info().getheader('Content-Length') + ' vs ' + str(originalSize) + "\n"
                        #return
                        finalChunkDifference = decrypt.decryptCalculatePadding(response,chunksize=CHUNK)
                        #xbmcplugin.playbackBuffer.playback[count]['length'] = int(xbmcplugin.playbackBuffer.playback[count]['length']) - finalChunkDifference
                        xbmcplugin.playbackBuffer.playback[count]['decryptedlength'] = int(xbmcplugin.playbackBuffer.playback[count]['length']) - finalChunkDifference - 8
                        newEnd = int(xbmcplugin.playbackBuffer.playback[count]['length'])- 1
                        returnLength = int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])

                        if constants.CONST.DEBUG:
                            print "FINAL CHUNK SIZE DIFFERENCE " + str(finalChunkDifference) + "\n"
                            print "length " +  str(xbmcplugin.playbackBuffer.playback[count]['length']) + "\n"
                            print "decryptedlength " +  str(xbmcplugin.playbackBuffer.playback[count]['decryptedlength']) + "\n"

                        response.close()



                #
                # 1) start > 16 bytes, back up to nearest whole chunk of 16
                if ((start != '' and start > 16) and (end == '' or end == int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])-1 )): # or end == (len -1)
                    newEnd = int(xbmcplugin.playbackBuffer.playback[count]['length'])-1
                    offset = (16-(newEnd - start + 8 +1) % 16)
                    newStart = start - offset + 8#0
                    returnLength = int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength']) - start
                    skip = 0
                    adjStart = offset #+8
                    adjEnd = 0
                    if constants.CONST.DEBUG:
                        print "[3] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"
                # 2) start = 0, fetch all, return all
                elif ( start == 0 and end != '' and end == int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])-1 ):
                    finalChunkDifference = int(xbmcplugin.playbackBuffer.playback[count]['length']) - int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])
                    newStart = 8 #=0
                    newEnd = int(xbmcplugin.playbackBuffer.playback[count]['length']) -1
                    returnLength = int(xbmcplugin.playbackBuffer.playback[count]['length']) - finalChunkDifference - 8
                    offset = 0
                    adjStart = 0
                    adjEnd = 0
                    if constants.CONST.DEBUG:
                        print "[2] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"
                # staart = 0, end < length -1
                elif ( start == 0 and end > 16 and end <= int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])-1 ):
                    newStart = 8#0
                    offset = (16 - (end - newStart + 1)%16)
                    newEnd = end + offset # +8
                    returnLength = end - start + 1
                    #skip = 8
                    adjStart = 0
                    adjEnd = offset#+8
                    if constants.CONST.DEBUG:
                        print "[4] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"

                #s > 0 e < len -1
                elif (start != '' and start > 16 and end <= int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])-1 ):

                    newStart = start - (start%16) + 8
                    #newStart = start + 8
                    #offset = 16 - (end  - start + 1)%16
                    #newEnd = end + offset + 8
                    newEnd = end + (16- (end%16)) + 8 -1
                    #if newEnd > int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])-1:
                    #    newEnd = end + 8
                    #    newStart = start - offset + 8
                    #    adjStart = offset
                    #    adjEnd = 0
                    #else:
                    #    adjStart = 0
                    #    adjEnd = offset
                    adjStart = start%16
                    adjEnd = 16 - end%16 -1
                    offset = 0
                    returnLength = end - start + 1
                    if constants.CONST.DEBUG:
                        print "[5] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"
                # special case - end < 16 (such as first 2 bytes (apple)
                elif (end < 16):
                    newStart = 8#0
                    newEnd = 15 + 8
                    returnLength = 2
                    adjStart = 0#8
                    adjEnd = 14
                    offset = 0
                    if constants.CONST.DEBUG:
                        print "[1] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"
              #  elif start == "":
              #      newStart = 8#0
              #      adjStart = 0#8
              #      adjEnd = 0
              #      offset = 0
              #      print "[0] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ", E*=TBD, returnLength=TBD\n"

                else:
                    newStart = 8#0
                    newEnd = int(xbmcplugin.playbackBuffer.playback[count]['length'])- 1
                    returnLength = int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])
                    adjStart = 0#8
                    adjEnd = 0
                    offset = 0
                    if constants.CONST.DEBUG:
                        print "[0] S=" + str(start) + ', E=' + str(end) + ', S*='+str(newStart)+ '('+str(adjStart)+') , offset=' +str(offset)+ ' , E*=' +str(newEnd) +'('+str(adjEnd)+'), returnLength='+str(returnLength)+"\n"


            if start == '' and not isEncrypted:
#                req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth})
                req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth})
            elif isEncrypted:
                req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth, 'Range': 'bytes='+str(newStart)+'-' + str(newEnd)})
            else:
                req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth, 'Range': 'bytes='+str(start)+'-' + str(end)})

            try:
                response = urllib2.urlopen(req)
                try:
                    if xbmcplugin.playbackBuffer.playback[count]['length'] == -1:
                        return
                except:
                    xbmcplugin.playbackBuffer.playback[count]['length'] =  response.info().getheader('Content-Length')

            except urllib2.URLError, e:
                if e.code == 403 or e.code == 401:
                    xbmc.log("STILL ERROR 111 " +url +str(e.code))
                    self.send_header('Cache-Control',response.info().getheader('Cache-Control'))
                    self.send_header('Date',response.info().getheader('Date'))
                    self.send_header('Content-type','video/mp4')
                    f =open('./resources/videos/transcode.mp4', 'rb')
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                    f.close()
                    self.send_header('Content-Length',str(size))
                    self.send_header('Content-Range','bytes 0 -' + str(int(size-1)) + '/' +  str(size))

                    self.end_headers()
                    with open('./resources/videos/transcode.mp4', 'rb') as f:
                        self.wfile.write(f.read())
                    f.close()
                    return
                else:
                    return


            if start == '':
                self.send_response(200)
                #self.send_header('Content-Length',response.info().getheader('Content-Length'))
                if isEncrypted:
                    self.send_header('Content-Length',xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])
                else:
                    self.send_header('Content-Length',xbmcplugin.playbackBuffer.playback[count]['length'])
            else:
                self.send_response(206)
                if isEncrypted:
                    self.send_header('Content-Length', str(returnLength))
                else:
                    self.send_header('Content-Length', str(int(response.info().getheader('Content-Length'))))

            xbmc.log( str(response.info()))
            self.send_header('Content-Type',response.info().getheader('Content-Type'))
            if isEncrypted:
                if end == '':
                    end = int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength']) - 1
                if start == '':
                    start = 0
                self.send_header('Content-Range','bytes ' + str(start) + '-' + str(end) + '/' +  str(int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])))
                if constants.CONST.DEBUG:
                    print "SENDING =" + 'bytes ' + str(start) + '-' + str(end) + '/' + str( int(xbmcplugin.playbackBuffer.playback[count]['decryptedlength'])) + "\n"
                #self.send_header('Content-Range', response.info().getheader('Content-Range'))
                if constants.CONST.DEBUG and response.info().getheader('Content-Range') != None:
                    print "received to process = " + response.info().getheader('Content-Range') + "\n"

            else:
                self.send_header('Content-Range', response.info().getheader('Content-Range'))
                #print "RANGE = " +  response.info().getheader('Content-Range') + "\n"

            self.send_header('Cache-Control',response.info().getheader('Cache-Control'))
            self.send_header('Date',response.info().getheader('Date'))
            self.send_header('Content-type','video/mp4')
            self.send_header('Accept-Ranges','bytes')

            self.end_headers()


            if isEncrypted:

                CHUNK = 16 * 1024
                decrypt.decryptStreamChunk(response,self.wfile, adjStart,adjEnd, chunksize=CHUNK)

            else:
                import time
                CHUNK = 16 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    # testing of rate limitator
                    ###time.sleep(0.02)
#                    if constants.CONST.DEBUG:
#                        print "HASH = " + str(hashlib.md5(chunk).hexdigest()) + "\n"






            #response_data = response.read()
            response.close()
            return



        # ** unauthenticated playback (don't require authentication)
        # mode=video and no other mode=
        # OR
        # mode=index and folder!=root
        elif ( (re.search(r'mode=video', str(decryptkeyvalue),re.IGNORECASE) and not re.search(r'mode=^[video]', str(decryptkeyvalue),re.IGNORECASE) ) or (re.search(r'mode=index', str(decryptkeyvalue),re.IGNORECASE) and not re.search(r'folder=root', str(decryptkeyvalue),re.IGNORECASE) )) :# and not re.search(r'folder=root', str(decryptkeyvalue),re.IGNORECASE))) :#or (re.search(r'mode=index', str(decryptkeyvalue),re.IGNORECASE) and not re.search(r'folder=root', str(decryptkeyvalue),re.IGNORECASE)  )) :
#            self.send_response(200)
#            self.end_headers()

            results = re.search(r'\?(.*)$', str(decryptkeyvalue))
            if results:
                query = str(results.group(1))
                xbmc.log("query = " +str(query))

            quality = str(self.cookieQuality(headers))
            if quality != '':
                query = query + quality
                self.override = True

            if '&override=true' in query:
                self.override = True


            mediaEngine = engine.contentengine()
            mediaEngine.run(self,query, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
            return

        #require authentication for all further requests
        elif not isLoggedIn and (self.server.username is not None and self.server.username != ''):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            self.wfile.write('<html><form action="/list" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
            return
        else:

            # passed a kill signal?
            if decryptkeyvalue == '/kill':

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                if (self.server.username is not None and self.server.username != ''):
                    self.wfile.write('<html><form action="/kill" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Stop Server"></form></html>')
                else:
                    self.wfile.write('<html><form action="/kill" method="post"><input type="submit" value="Stop Server"></form></html>')

                #self.server.ready = False
                return


            # force refresh of scheduler
            elif  re.search(r'/default.py\?mode\=scheduler', str(decryptkeyvalue),re.IGNORECASE):

                self.server.addon = constants.addon
                self.server.addon.__init__()
                self.server.setDBM()

                results = re.search(r'\?(.*)$', str(decryptkeyvalue))
                if results:
                    query = str(results.group(1))

                mediaEngine = engine.contentengine()
                mediaEngine.run(self,query, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
                return


            # enroll read/write token
            elif  re.search(r'/default.py\?mode\=enroll_rw', str(decryptkeyvalue),re.IGNORECASE):

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                #pull client secrets

                self.wfile.write('<html><body>Two steps away.<br/><br/>  1) Visit this site and then paste the application code in the below form: <a href="https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/drive&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&client_id=772521706521-bi11ru1d9h40h1lipvbmp3oddtcgro14.apps.googleusercontent.com" target="new">Google Authentication</a><br /><br />2) Return back to this tab and provide a nickname and the application code provided in step 1. <form action="default.py?mode=enroll" method="post">Nickname for account:<br /><input type="text" name="account"><br />Code (copy and paste from step 1):<br /><input type="text" name="code"><br /><form action="default.py?mode=enroll" method="post">Client ID:<br /><input type="hidden" name="client_id" value="772521706521-bi11ru1d9h40h1lipvbmp3oddtcgro14.apps.googleusercontent.com"><br />Client Secret:<br /><input type="hidden" name="client_secret" value="PgteSoD4uagqHA1_nLERLDx9"><br /><br /></br /> <input type="submit" value="Submit"></form></body></html>')
                return


            # redirect url to output
            elif  re.search(r'/default.py\?mode\=enroll\&default\=true', str(decryptkeyvalue),re.IGNORECASE):# or  re.search(r'/default.py\?mode\=enroll', str(decryptkeyvalue)):

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                self.wfile.write('<html><body>Two steps away.<br/><br/>  1) Visit this site and then paste the application code in the below form: <a href="https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/drive&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&client_id=772521706521-bi11ru1d9h40h1lipvbmp3oddtcgro14.apps.googleusercontent.com" target="new">Google Authentication</a><br /><br />2) Return back to this tab and provide a nickname and the application code provided in step 1. <form action="default.py?mode=enroll" method="post">Nickname for account:<br /><input type="text" name="account"><br />Code (copy and paste from step 1):<br /><input type="text" name="code"><br /><form action="default.py?mode=enroll" method="post">Client ID:<br /><input type="hidden" name="client_id" value="772521706521-bi11ru1d9h40h1lipvbmp3oddtcgro14.apps.googleusercontent.com"><br />Client Secret:<br /><input type="hidden" name="client_secret" value="PgteSoD4uagqHA1_nLERLDx9"><br /><br /></br /> <input type="submit" value="Submit"></form></body></html>')
                return

            # redirect url to output
            elif  re.search(r'/default.py\?mode\=enroll', str(decryptkeyvalue),re.IGNORECASE):

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                self.wfile.write('<html><body>Do you want to use a default client id / client secret or your own client id / client secret?  If you don\'t know what this means, select DEFAULT.<br /> <a href="default.py?mode=enroll&default=true">use default client id / client secret (DEFAULT)</a> <br /><br />OR use your own client id / client secret<br /><br /><form action="default.py?mode=enroll&default=false" method="post">Client ID:<br /><input type="text" name="client_id" value=""><br />Client Secret:<br /><input type="text" name="client_secret" value=""> <br/><input type="submit" value="Submit"></form></body></html>')
                return

            elif  re.search(r'/default.py\?mode\=enroll\&default\=false', str(decryptkeyvalue),re.IGNORECASE):

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                self.wfile.write('<html><body>Two steps away.<br/><br/>  1) Visit this site and then paste the application code in the below form: <a href="https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/drive&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&client_id=772521706521-bi11ru1d9h40h1lipvbmp3oddtcgro14.apps.googleusercontent.com" target="new">Google Authentication</a><br /><br />2) Return back to this tab and provide a nickname and the application code provided in step 1. <form action="default.py?mode=enroll" method="post">Nickname for account:<br /><input type="text" name="account"><br />Code (copy and paste from step 1):<br /><input type="text" name="code"><br /><br /> <input type="submit" value="Submit"></form></body></html>')
                return


            elif  re.search(r'/settings', str(decryptkeyvalue),re.IGNORECASE):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                    self.wfile.write('<html><form action="/settings" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
                else:
                    self.displaySettings(host=host)

                #self.server.ready = False
                return




            elif decryptkeyvalue == '/list' or decryptkeyvalue == '/':

                if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write('<html><form action="/list" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
                else:
                    mediaEngine = engine.contentengine()
                    mediaEngine.run(self, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)

                #self.server.ready = False
                return

            elif decryptkeyvalue == '/reload':
                self.server.addon = constants.addon
                self.server.addon.__init__()
                self.server.setDBM()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                    self.wfile.write('<html><form action="/list" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
                else:
                    self.wfile.write('<html><form action="/list" method="post"><input type="submit" value="Login"></form></html>')

                #self.server.ready = False
                return

            elif decryptkeyvalue == '/reloadhash':

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.server.loadHash(True)
                if not isLoggedIn and (self.server.username is not None and self.server.username != ''):
                    self.wfile.write('<html><form action="/list" method="post">Username: <input type="text" name="username"><br />Password: <input type="password" name="password"><br /><input type="submit" value="Login"></form></html>')
                else:
                    self.wfile.write('<html><form action="/list" method="post"><input type="submit" value="Login"></form></html>')

                return




            # redirect url to output
            elif re.search(r'/\?', str(decryptkeyvalue)) or re.search(r'/default.py', str(decryptkeyvalue),re.IGNORECASE):
    #            self.send_response(200)
    #            self.end_headers()

                results = re.search(r'\?(.*)$', str(decryptkeyvalue))
                if results:
                    query = str(results.group(1))
                    xbmc.log("query = " +str(query))

                quality = str(self.cookieQuality(headers))
                if quality != '':
                    query = query + quality
                    self.override = True

                if '&override=true' in query:
                    self.override = True


                mediaEngine = engine.contentengine()
                mediaEngine.run(self,query, DBM=self.server.dbm, addon=self.server.addon, host=host, MD5List=self.server.MD5List, fileIDList=self.server.fileIDList)
                return





    def displaySettings(self, host=''):


            self.wfile.write('<html><form autocomplete="off" action="/save_settings" method="post">')

            self.wfile.write('<h1>Plugin Configuration:</h1><hr align="left" width="400">')
            self.wfile.write('<b>Secure Login</b><br />Username <input name="username" type="text" value="'+str(self.server.dbm.getSetting('username',default=''))+'" /><br />')
            self.wfile.write('Password <input name="passwrd" type="text" value="'+str(self.server.dbm.getSetting('password',default=''))+'" /><br />')
            self.wfile.write('<br /><input type="submit" value="Save" />')

            self.wfile.write('<hr align="left" width="400">Server log <input name="logfile" type="text" value="'+str(self.server.dbm.getSetting('logfile',default=''))+'" /> <sub>[eneter a path such as /tmp/server.log]</sub><br />')
            self.wfile.write('Scheduler log <input name="scheduler_logfile" type="text" value="'+str(self.server.dbm.getSetting('scheduler_logfile',default=''))+'" /> <sub>[eneter a path such as /tmp/scheduler.log]</sub><br />')
            self.wfile.write('Debug mode <select name="debug">')
            if self.server.dbm.getSetting('debug') == 'true':
                self.wfile.write('<option value="true" selected >true</option><option value="false">false</option><br /></select>')
            else:
                self.wfile.write('<option value="true">true</option><option value="false" selected>false</opton><br /></select>')

            self.wfile.write('<br /><input type="submit" value="Save" />')

            self.wfile.write('<br /><hr align="left" width="400"><b><i>The following settings affect creating secure URLs:</i></b><br />Hide parameters <select name="hide">')
            if self.server.dbm.getSetting('hide') == 'true':
                self.wfile.write('<option value="true" selected >true</option><option value="false">false</option><br /></select>')
            else:
                self.wfile.write('<option value="true">true</option><option value="false" selected>false</opton><br /></select>')
            self.wfile.write('<br />Generate keyvalue parameters <select name="keyvalue">')
            if self.server.dbm.getSetting('keyvalue') == 'true':
                self.wfile.write('<option value="true" selected >true</option><option value="false">false</option><br /></select>')
            else:
                self.wfile.write('<option value="true">true</option><option value="false" selected>false</opton><br /></select>')

            self.wfile.write('<br />Salt file <input name="saltfile" type="text" value="'+str(self.server.dbm.getSetting('saltfile',default='saltfile'))+'"><sub>[eneter a path such as /var/saltfile]</sub>')
            self.wfile.write('<br />Salt password <input name="saltpassword" type="text" value="'+str(self.server.dbm.getSetting('saltpassword',default='saltpassword'))+'">')

            self.wfile.write('<br /><input type="submit" value="Save" />')
            self.wfile.write('<h1>Media Configuration:</h1><hr align="left" width="400">')
            self.wfile.write('<br />Passthrough <select name="passthrough">')
            if self.server.dbm.getSetting('passthrough') == 'true':
                self.wfile.write('<option value="true" selected >true</option><option value="false">false</option><br /></select>')
            else:
                self.wfile.write('<option value="true" selected>true</option><option value="false">false</opton><br /></select>')

            self.setings = {}
            file = open('./resources/settings.xml', "r")
            for line in file:

                id = ''
                type = ''
                values = ''
                default = ''
                label = ''
                range = ''
                #special override -- display all files within video view
                if id == 'context_video':
                    default = 2
                result = re.search(r'\<setting id\=\"([^\"]+)\" type\=\"([^\"]+)\" values\=\"([^\"]*)\" default\=\"([^\"]*)\" label\=\"(\d+)\" \/\>', str(line))
                if result:
                    id = str(result.group(1))
                    type = str(result.group(2))
                    values = str(result.group(3))
                    default = str(result.group(4))
                    label = str(result.group(5))
                if result is None:
                    result = re.search(r'\<setting id\=\"([^\"]+)\" type\=\"([^\"]+)\"[^/]+label\=\"(\d+)\" default\=\"([^\"]*)\" option\=\"([^\"]*)\" range\=\"([^\"]*)\"[^/]+\/\>\n', str(line))
                    if result:
                        id = str(result.group(1))
                        type = str(result.group(2))
                        default = str(result.group(4))
                        label = str(result.group(3))
                        range = str(result.group(6))
                if result is None:
                    result = re.search(r'\<setting id\=\"([^\"]+)\" type\=\"([^\"]+)\"[^/]+label\=\"(\d+)\" default\=\"([^\"]*)\"([^/]+)\/\>\n', str(line))
                    if result:
                        id = str(result.group(1))
                        type = str(result.group(2))
                        default = str(result.group(4))
                        label = str(result.group(3))

                if result is None:
                    result = re.search(r'\<setting id\=\"([^\"]+)\" type\=\"([^\"]+)\".*?label\=\"(\d+)\" values\=\"([^\"]*)\" default\=\"([^\"]*)\"[^\/]* \/\>\n', str(line))
                    if result:
                        id = str(result.group(1))
                        type = str(result.group(2))
                        default = str(result.group(5))
                        label = str(result.group(3))
                        values = str(result.group(4))

                #<setting label="30205" type="lsep"/>
                if result is None:
                    result = re.search(r'\<setting.*label\=\"(\d+)\" type\=\"lsep\"\/\>\n', str(line))
                    if result:
                        label = str(result.group(1))
                        self.wfile.write(str('<br /><b>' + self.server.addon.getLocalizedString(label)) + '</b><br /> ')
                #    <category label="30196">
                if result is None:
                    result = re.search(r'\<category label\=\"(\d+)\"\>\n', str(line))
                    if result:
                        label = str(result.group(1))
                        self.wfile.write(str('<input type="submit" value="Save" /><h2>' + self.server.addon.getLocalizedString(label)) + '</h2>')

                if result:
                    if id != '':
                        currentValue = self.server.dbm.getSetting(id)
                        if currentValue is None:
                            currentValue = default
                        if type == 'text' or type == 'number':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <input name="'+str(id)+'" type="text" value="'+str(currentValue)+'" /><br />')
                        if type == 'file' or type == 'folder':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <input name="'+str(id)+'" type="text" value="'+str(currentValue)+'" /> <sub>[select server path to '+str(type)+']</sub><br />')
                        elif type == 'labelenum':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <select name="'+str(id)+'">')

                            for r in re.finditer('(\d+)(?:\||$)' ,
                                             values, re.DOTALL):
                                if r.group(1) == int(currentValue):
                                    self.wfile.write('<option value="'+str(r.group(1))+'" selected/>'+str(r.group(1)) + '</option>')
                                else:
                                    self.wfile.write('<option value="'+str(r.group(1))+'"/>'+str(r.group(1)) + '</option>')

                            self.wfile.write('</select><br />')
                        elif type == 'enum':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <select name="'+str(id)+'">')

                            count = 0
                            for r in re.finditer('([^\|]+)(?:\||$)' ,
                                             values, re.DOTALL):

                                if count == int(currentValue):
                                    self.wfile.write('<option value="'+str(count)+'" selected/>'+str(r.group(1)) + '</option>')
                                else:
                                    self.wfile.write('<option value="'+str(count)+'"/>'+str(r.group(1)) + '</option>')
                                count += 1

                            self.wfile.write('</select><br />')
                        elif type == 'slider':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <select name="'+str(id)+'">')

                            for r in re.finditer('(\d+)\,(\d+)\,(\d+)' ,
                                             range, re.DOTALL):

                                min = int(r.group(1))
                                increment = int(r.group(2))
                                max = int(r.group(3))
                                i = min
                                while i < max:

                                    if i == int(currentValue):
                                        self.wfile.write('<option value="'+str(i)+'" selected/>'+str(i) + '</option>')
                                    else:
                                        self.wfile.write('<option value="'+str(i)+'"/>'+str(i) + '</option>')
                                    i = i + increment
                            self.wfile.write('</select><br />')

                        elif type == 'bool':
                            self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+') <select name="'+str(id)+'"/>')
                            if currentValue == 'true':
                                #self.wfile.write(str(self.server.addon.getLocalizedString(label)) + ' ('+str(id)+')<input name="'+str(id)+'" type="checkbox" value="true" checked /><br />')
                                self.wfile.write('<option value="true" selected/>true</option>')
                                self.wfile.write('<option value="false"/>false</option>')
                            else:
                                self.wfile.write('<option value="false" selected/>false</option>')
                                self.wfile.write('<option value="true"/>true</option>')

                            self.wfile.write('</select><br />')
            self.wfile.write('<br />Hostname <input name="hostname" type="text" value="'+str(self.server.dbm.getSetting('host', default=host))+'" /><br />')
            self.wfile.write('<input type="submit" value="Save" /></form></html>')

    def cookieLogin(self,headers):

        if headers is None:
            return False
        for r in re.finditer('Cookie\:[^\n]+login\=(\S+)' ,
                     str(headers), re.DOTALL):
          loginSession = r.group(1)
          try:
              if self.server.logins[loginSession] == 1:
                  return True
          except:
              return False

    def cookieQuality(self,headers):

        if headers is None:
            return ''
        for r in re.finditer('Cookie\:[^\n]+quality\=(\d+)' ,
                     str(headers), re.DOTALL):
          quality = r.group(1)
          return '&override=true&preferred_quality=' + str(quality)
        return ''


