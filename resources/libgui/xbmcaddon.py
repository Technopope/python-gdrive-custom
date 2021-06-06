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

import anydbm
import re
import os

from resources.libgui import settingsdbm
# The purpose of this class is to override  xbmcaddon and supply equivalent subroutines when ran without KODI
#

class getAddonInfo(object):

    def ok(self, heading, line1, line2='', line3=''):
        return



class xbmcaddon:
    # CloudService v0.3.0

    ##
    ##
    def __init__(self, dbm=None):

        if dbm is None:
            self.dbm = settingsdbm.settingsdbm('./gdrive.db')
            #self.dbmfile = './gdrive.db'
            #if os.path.exists(self.dbmfile):
            #    self.dbm = anydbm.open(self.dbmfile,'r')
            #else:
            #    self.dbm = anydbm.open(self.dbmfile,'c')
        else:
            self.dbm = dbm

        self.language = {}
        try:
            file = open('./resources/language/english/strings.xml', "r")
            for line in file:
                result = re.search(r'\<string id\=\"([^\"]+)\"\>([^\<]+)\<', str(line))
                key = ''
                value = ''
                if result:
                    key = str(result.group(1))
                    value = str(result.group(2))
                    self.language[key] = value;
        except:
            pass




        return

    def getAddonInfo(self, id):
        return ''



    ##
    # return the setting from DBM
    ##
    def getSetting(self,key, default=None, forceSync=False):

        return self.dbm.getSetting(key,default=default, forceSync=forceSync)

        try:
            self.dbm.sync()
        except:
            self.dbm = anydbm.open(self.dbmfile,'r')
        try:
            return self.dbm[key]
        except:
            return default



    ##
    # return the setting from DBM
    ##
    def setSetting(self,key,value, forceSync=False):
        return self.dbm.setSetting(key,value, forceSync=forceSync)

        self.dbm.close()
        self.dbm = anydbm.open(self.dbmfile,'w')
        self.dbm[key] = value
        try:
            self.dbm.sync()
        except:
            pass
        self.dbm.close()
        #self.dbm = anydbm.open(self.dbmfile,'r')
        return


    ##
    # return the language setting
    ##
    def getLocalizedString(self,key):
        return self.language[str(key)]


