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
import anydbm
import os

class settingsdbm:
    # Settings

    ##
    ##
    def __init__(self, dbmfile):

        self.dbmfile = dbmfile
        #setup encryption password

        try:
            self.dbm = anydbm.open(dbmfile,'r')
        except:
            self.dbm = anydbm.open(dbmfile,'c')

        self.isReadOnly = True


    def reset(self):
        self.dbm.close()
        try:
            self.dbm = anydbm.open(self.dbmfile,'r')
        except:
            self.dbm = anydbm.open(self.dbmfile,'c')

        self.isReadOnly = True


    def getSetting(self, key, default=None, forceSync=False):
        if not self.isReadOnly:
            self.dbm.close()
            try:
                self.dbm = anydbm.open(self.dbmfile,'r')
            except:
                self.dbm = anydbm.open(self.dbmfile,'c')

            self.isReadOnly = True

#        if forceSync:
            #self.dbm.sync()

        if key is '':
            return None
        try:
            return self.dbm[key]
        except:
            return default

    def getBoolSetting(self, key, default=None, forceSync=False):
        if not self.isReadOnly:
            self.dbm.close()
            try:
                self.dbm = anydbm.open(self.dbmfile,'r')
            except:
                self.dbm = anydbm.open(self.dbmfile,'c')

            self.isReadOnly = True

#        if forceSync:
#            self.dbm.sync()

        if key is '':
            return None
        try:
            value = self.dbm[key]
            if value == 'True' or value == 'true':
                return True
            else:
                return False
        except:
            return default

    def getIntSetting(self, key, default=None, forceSync=False):
        if not self.isReadOnly:
            #self.dbm.sync()
            self.dbm.close()
            try:
                self.dbm = anydbm.open(self.dbmfile,'r')
            except:
                self.dbm = anydbm.open(self.dbmfile,'c')

            self.isReadOnly = True

 #       if forceSync:
 #           self.dbm.sync()

        if key is '':
            return None
        try:
            return int(self.dbm[key])
        except:
            return default

    def setSetting(self, key, value, forceSync=False):
        if self.isReadOnly:
            self.dbm.close()
            try:
                self.dbm = anydbm.open(self.dbmfile,'w')
            except:
                self.dbm = anydbm.open(self.dbmfile,'c')

            self.isReadOnly = False

        if forceSync:
            try:
                self.dbm.sync()
            except:
                pass

        self.dbm[key] = value
        #self.dbm.sync()

        return

