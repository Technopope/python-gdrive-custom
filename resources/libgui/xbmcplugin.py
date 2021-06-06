'''
    Copyright (C) 2014-2017 ddurdle

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

import re
import urllib, urllib2

from resources.libgui import xbmc

class outputBuffer(object):
    output = ''
    writer = ''

class playbackBuffer(object):
    playback =[]

class instanceSettings(object):
    keypair = True

#
# The purpose of this class is to override  xbmcgui and supply equivalent subroutines when ran without KODI
#

class addSortMethod(object):

    def ok(self):
        return



class addDirectoryItem(object):

    def __init__(self,plugin_handle, url, listitem, isFolder=None, totalItems=None):
        label = str(listitem)
        label = label.replace("<",'(')
        label = label.replace(">",')')

        if url != '' and (plugin_handle.server.keyvalue or plugin_handle.server.hide) and plugin_handle.server.encrypt is not None  and plugin_handle.server.encrypt.ENCRYPTION_ENABLE == 1:
            params = re.search(r'^([^\?]+)\?([^\?]+)$', str(url))

            if params and plugin_handle.server.hide:
                base = str(params.group(1))
                extended = str(params.group(1))
                url = str(base) + '?kv=' +plugin_handle.server.encrypt.encryptString(url)
            else:
                url = str(url) + '&kv=' +plugin_handle.server.encrypt.encryptString(url)

        if listitem.thumbnailImage is not None:
            outputBuffer.output =  outputBuffer.output + "<a href=\"" + str(url)+ "\"><img src=\""+listitem.thumbnailImage+"\" /><br />"+ str(label) + "</a>"+ listitem.detail+  listitem.menu+"<br />\n"
        else:
            outputBuffer.output =  outputBuffer.output + "<a href=\"" + str(url)+ "\">"+ str(label) + "</a> "+ listitem.menu+"<br />\n"
        return

class endOfDirectory(object):

    def __init__(self,plugin_handle):
        if plugin_handle is not None:
            plugin_handle.send_response(200)
            plugin_handle.end_headers()
            plugin_handle.wfile.write('<html>'+outputBuffer.output+'</html>')
            outputBuffer.output = ''


        return

class setResolvedUrl(object):

    def __init__(self,plugin_handle,value2,item, encrypted=False):
        if plugin_handle is not None:

            plugin_handle.send_response(307)
            url = ''
            cookie = ''
            auth = ''
            playbackURL = ''
            for r in re.finditer('^([^\|]+)\|' ,
                     item.path, re.DOTALL):
                url = r.group(1)
#                plugin_handle.send_header('Set-Cookie', 'url='+url)

            for r in re.finditer('Cookie\=DRIVE_STREAM%3D([^\&]+)' ,
                     item.path, re.DOTALL):
                cookie = r.group(1)
#                plugin_handle.send_header('Set-Cookie', cookie)
            for r in re.finditer('Authorization\=([^\s]+)' ,
                     item.path, re.DOTALL):
                auth = r.group(1)
#                plugin_handle.send_header('Set-Cookie', auth)

            playbackBuffer.playback.append({'auth':auth,'url':url,'cookie':cookie})
            #auth = auth.replace("+",' ')
            #plugin_handle.send_header('Authorization', auth)
            if not plugin_handle.override and not encrypted and (plugin_handle.server.addon.getSetting('passthrough')) == 'true':
                auth = auth.replace("Bearer+",'')
                playbackURL = url + '&access_token='+auth

            elif encrypted:
                playbackURL = '/play?count=' + str(len(playbackBuffer.playback)-1) + '&encrypted=true'

            else:
                playbackURL = '/play?count=' + str(len(playbackBuffer.playback)-1)
            plugin_handle.send_header('Location', playbackURL)
            xbmc.log("setResolvedUrl - resolving to URL = " + playbackURL, xbmc.LOGDEBUG)
            plugin_handle.end_headers()



            if 0:

                headers = str(plugin_handle.headers) + "\n"
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

    #            plugin_handle.send_response(302)
                for r in re.finditer('^([^\|]+)\|' ,
                         item.path, re.DOTALL):
                    url = r.group(1)
    #                plugin_handle.send_header('Set-Cookie', 'url='+url)

                for r in re.finditer('Cookie\=DRIVE_STREAM%3D([^\&]+)' ,
                         item.path, re.DOTALL):
                    cookie = r.group(1)
    #                plugin_handle.send_header('Set-Cookie', cookie)
                for r in re.finditer('Authorization\=([^\s]+)' ,
                         item.path, re.DOTALL):
                    auth = r.group(1)
    #                plugin_handle.send_header('Set-Cookie', auth)
    #            plugin_handle.send_header('Location', '/play')
                #plugin_handle.end_headers()

                if start == '':
                    req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth})
                else:
                    req = urllib2.Request(url,  None,  { 'Cookie' : 'DRIVE_STREAM='+ cookie, 'Authorization' : auth, 'Range': 'bytes='+str(start- startOffset)+'-' + str(end)})


                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                    if e.code == 403 or e.code == 401:
                        xbmc.log("STILL ERROR")
                        return
                    else:
                        return
                plugin_handle.server.length = response.info().getheader('Content-Length')

                if start == '':
                    plugin_handle.send_response(200)
                    plugin_handle.send_header('Content-Length',response.info().getheader('Content-Length'))
                else:
                    plugin_handle.send_response(206)
                    plugin_handle.send_header('Content-Length', str(int(response.info().getheader('Content-Length'))-startOffset))
                    plugin_handle.send_header('Content-Range', response.info().getheader('Content-Range'))
                    #self.send_header('Content-Range','bytes ' + str(start) + '-' +str(end))
                    #if end == '':
                    #    plugin_handle.send_header('Content-Range','bytes ' + str(start) + '-' +str(int(plugin_handle.server.length)-1) + '/' +str(int(plugin_handle.server.length)))
                    #else:
                    #    plugin_handle.send_header('Content-Range','bytes ' + str(start) + '-' + str(end) + '/' +str(int(plugin_handle.server.length)))

                    #self.send_header('Content-Range',response.info().getheader('Content-Range'))


                print str(response.info()) + "\n"
                plugin_handle.send_header('Content-Type',response.info().getheader('Content-Type'))

                plugin_handle.send_header('Cache-Control',response.info().getheader('Cache-Control'))
                plugin_handle.send_header('Date',response.info().getheader('Date'))
                plugin_handle.send_header('Content-type','video/mp4')
                plugin_handle.send_header('Accept-Ranges','bytes')

                plugin_handle.end_headers()

                CHUNK = 16 * 1024
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    plugin_handle.wfile.write(chunk)

                #response_data = response.read()
                response.close()


        return

class assignOutputBuffer(object):

    def __init__(self,writer):
        outputBuffer.writer = writer
        return


class xbmcplugin:
    # CloudService v0.3.0

    ##
    ##
    def __init__(self):
        self.Dialog.ok = None
        return


