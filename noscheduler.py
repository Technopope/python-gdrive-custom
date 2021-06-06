'''
    CloudService XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

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
from resources.libgui import webgui
import urllib, urllib2
import httplib
from SocketServer import ThreadingMixIn
import threading
import sys
import os
import time
from datetime import datetime
import re
from resources.libgui import settingsdbm
from resources.lib import scheduler

#from multiprocessing import Process


if __name__ == '__main__':


    # default.py [settings-dbm] [PORT] [SSL-certificate]
    try:
        port = int(sys.argv[2])
    except:
        port = 9988
    try:
        dbmfile = str(sys.argv[1])
    except:
        dbmfile = './gdrive.db'

    try:
        sslcert = str(sys.argv[3])
    except:
        sslcert = None

    try:
        import faulthandler
        faulthandler.enable()
        print('Faulthandler enabled')
    except Exception:
        print('Could not enable faulthandler')

    #try:
    server = webgui.WebGUIServer(('',  port), webgui.webGUI)
    if sslcert is not None:
        import ssl
        server.socket = ssl.wrap_socket (server.socket, certfile=sslcert, server_side=True)

    server.setDBM(dbmfile)
    server.setPort(port)

    print "Google Drive Media Server ready (NO SCHEDULER)....\n"



    while server.ready:
        server.handle_request()
    server.socket.close()



#except: pass

#default.run()
