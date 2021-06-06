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


def job_scheduler(server, sleepTimer):
    dbm = server.dbm
    schedule = scheduler.scheduler(logfile=dbm.getSetting('scheduler_logfile', None))

    i=0
    while 1:
        runtime = dbm.getIntSetting(str(i)+'_runtime', None)
        status = dbm.getIntSetting(str(i)+'_status', None)
        if runtime is None:
            i += 1
            break
        elif status == 1:
            schedule.log ("job #" + str(i)+ " is detected as incomplete")
            dbm.setSetting(str(i)+'_status', str(0))
        i += 1


    while 1:
        i=0
        currentTime = int(time.time())
        while 1:
            runtime = dbm.getIntSetting(str(i)+'_runtime', None)
            instance = dbm.getSetting(str(i)+'_instance', None)
            if runtime is None and instance is None:
                i += 1
                break
            if instance is not None and instance != '':
                frequency = dbm.getIntSetting(str(i)+'_frequency', None)
                status = dbm.getIntSetting(str(i)+'_status', None)
                type = dbm.getIntSetting(str(i)+'_type', None)
                folderID = dbm.getSetting(str(i)+'_folder', None)
                instanceName = dbm.getSetting(str(i)+'_instance', None)

                if status is None:
                    schedule.log ("status = " + str(status) + 'job' + str(i))
                elif status == 0 and frequency is not None and runtime < (currentTime - (frequency*60)) :
                    cmd = dbm.getSetting(str(i)+'_cmd', None)
                    schedule.log ("time to run job #" + str(i) + ' runtime ' + str(runtime) + ' test ' + str(currentTime - (frequency*60))+  'cmd' + str(cmd))

                    if cmd is not None:
                        currentTime = int(time.time())
                        dbm.setSetting(str(i)+'_runtime', str(currentTime))
                        dbm.setSetting(str(i)+'_status', str(1))
                        schedule.log('runtime & status updated')

                        #do a full sync only
                        #if type == schedule.SYNC_BOTH and (runtime is None or runtime == 0):
                        #    dbm.setSetting(str(i)+'_type', str(schedule.SYNC_INITIAL_ONLY))


                        cmd = re.sub('buildstrmscheduler', 'buildstrm', cmd)
                        cmd = re.sub('#', '%23%0A2', cmd)
                        cmd = re.sub(' ', '%20', cmd)
                        changeToken = dbm.getSetting(str(instanceName) +'_'+str(folderID)+'_changetoken', '')
                        # first run, run full don't do change tracking
                        if not  type == schedule.SYNC_INITIAL_ONLY and not (type == schedule.SYNC_BOTH and (runtime is None or runtime == 0)):
                            cmd = cmd + '&changes=True'
                        if type != schedule.SYNC_INITIAL_ONLY and changeToken != '' and changeToken != '0':
                            cmd = cmd + '&change_token=' + str(changeToken)

                        schedule.log('making call to API')
                        if bool(re.match('^http', cmd, re.I)) :
                            try:
                                contents = urllib2.urlopen(cmd).read()
                            except:
                                contents  = 'exception'
                                schedule.log('exception making call to ' + str(cmd))

                        else:
                            try:
                                contents = urllib2.urlopen('http://'+str(cmd)).read()
                            except urllib2.HTTPError, e:
                                contents  = 'exception'
                                schedule.log('exception: ' + str(e.code))
                            except urllib2.URLError, e:
                                contents  = 'exception'
                                schedule.log('exception: ' + str(e.reason))
                            except httplib.HTTPException, e:
                                contents  = 'exception'
                                schedule.log('exception making call to http://' + str(cmd) + ', giving up.')
                            except:
                                contents = 'exception'
                                schedule.log('exception making call to http://' + str(cmd) + ', trying https')
                                try:
                                    contents = urllib2.urlopen('https://'+str(cmd)).read()
                                except:
                                    contents = 'exception'
                                    schedule.log('exception making call to http://' + str(cmd) + ', trying https')


                        contents = re.sub('<[^<]+?>', '', contents)
                        schedule.log(contents)
                        results = re.search(r'\(changetoken = ([^\)]+)\)', contents)
                        if results is not None and results.group(1) != changeToken:
                            dbm.setSetting(str(instanceName) +'_'+str(folderID)+'_changetoken', str(results.group(1)))
                            schedule.log(str(instanceName) +'_'+str(folderID)+'_changetoken' +  str(results.group(1)))
                        currentTime = int(time.time())
                        dbm.setSetting(str(i)+'_runtime', str(currentTime))
                        dbm.setSetting(str(i)+'_status', str(0))
                        if type == schedule.SYNC_BOTH and (runtime is None or runtime == 0):
                            dbm.setSetting(str(i)+'_type', str(schedule.SYNC_CHANGE_ONLY))
                        dbm.setSetting(str(i)+'_statusDetail', str(datetime.now()) + ' - ' + str(contents), forceSync=True)

                #else:
                #    schedule.log ("status = " + str(status))

            i += 1

        time.sleep(60)

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

    print "Google Drive Media Server ready....\n"



    #p.join()
    pid =1
    try:
        #p = Process(target=job_scheduler, args=(server, 60))
        #p.start()
        pid = os.fork()
    except:
        pass
    if pid == 0:
        job_scheduler(server,60)
    else:
        while server.ready:
            server.handle_request()
        server.socket.close()



#except: pass

#default.run()
