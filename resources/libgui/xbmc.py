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


#
# The purpose of this class is to override  xbmcgui and supply equivalent subroutines when ran without KODI
#


class Player(object):

    def play(self, url, item):
        setResolvedUrl(url,item)
        return

class openLog(object):
    ##
    def __init__(self,filename, debug=False):

        if filename is not None and filename != "":
            try:
                logfile.pipe = open(filename, "a")
            except:
                logfile.pipe = open(filename, "w")

        if debug:
            logfile.debug = True


class logfile(object):
    ##
    pipe = None
    debug = False


class log(object):
    ##
    def __init__(self,message,type=None):
        DEBUG = ''
        if type == LOGDEBUG and not logfile.debug:
            return
        elif logfile.debug and type == LOGDEBUG:
            DEBUG = 'debug - '


        if logfile.pipe is not None:
            logfile.pipe.write(DEBUG + str(message)+ "\n")
            logfile.pipe.flush()
        else:
            print DEBUG + str(message) + "\n"
        return

class sleep(object):
    ##
    def __init__(self,time):
        return


def translatePath(path):
    return path

class executebuiltin(object):
    ##
    def __init__(self,message):
#        if message == 'XBMC.Container.Refresh':
#            plugin_handle.send_header('Location', '/list')

        return

class LOGNOTICE(object):
    ##
    def __init__(self,message):
        return

LOGDEBUG = 1
LOGERROR = 2

class xbmc:
    # CloudService v0.3.0



    ##
    ##
    def __init__(self):
        self.Dialog.ok = None
        self.x = "XXX"
        return




    ##
    # Get the token of name with value provided.
    # returns: str
    ##
    def getToken(self,name):
        if name in self.auth:
            return self.auth[name]
        else:
            return ''

    ##
    # Get the count of authorization tokens
    # returns: int
    ##
    def getTokenCount(self):
        return len(self.auth)

    ##
    # Save the latest authorization tokens
    ##
    def saveTokens(self,instanceName,addon):
        for token in self.auth:
            addon.setSetting(instanceName + '_'+token, self.auth[token])

    ##
    # load the latest authorization tokens
    ##
    def loadToken(self,instanceName,addon, token):
        try:
            tokenValue = addon.getSetting(instanceName + '_'+token)
            if tokenValue != '':
              self.auth[token] = tokenValue
              return True
            else:
              return False
        except:
            return False

    ##
    # load the latest authorization tokens
    ##
    def isToken(self,instanceName, addon, token):
        try:
            if self.auth[token] != '':
              return True
            else:
              return False
        except:
            return False



