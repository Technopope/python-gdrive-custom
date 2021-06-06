
import sys
import re
import os

import anydbm

try:
    dbmfile = str(sys.argv[1])
    settingsfile = str(sys.argv[2])

    dbm = anydbm.open(dbmfile,'c')

    file = open(settingsfile, "r")
    print "saving the following key,value pairs\n"
    for line in file:
        result = re.search(r'\<setting id\=\"([^\"]+)\" value\=\"([^\"]+)" \/\>', str(line))
        key = ''
        value = ''
        if result:
            key = str(result.group(1))
            value = str(result.group(2))
            print str(key) + ',' + str(value) + "\n"
            dbm[key] = value;


    dbm.close()
except:
    print "This tool loads your KODI GDrive plugin settings to the DBM file.\nUsage:\n"
    print "python dbm_import.py <dbm_file.db> <settings.xml>"
