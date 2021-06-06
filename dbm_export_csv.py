
import sys
import re
import os

import anydbm

try:
    dbmfile = str(sys.argv[1])
    csvfile = str(sys.argv[2])
except:
    print "This tool exports your dbm to CSV format.  This can be used to recover data from a corrupt dbm.\nUsage:\n"
    print "python dbm_export_csv.py <dbm_file.db> <settings.csv>"

dbm = anydbm.open(dbmfile,'r')

file = open(csvfile, "w")
print "exporting the following key,value pairs\n"
for key in dbm:
    try:
        value = dbm[key];
    except:
        value = '***corrupt***'
    print str(key) + ',' + str(value) + "\n"
    file.write(str(key) + ',' + str(value) + "\n")

file.close()
dbm.close()
