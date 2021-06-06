
import sys
import re
import os

import anydbm

try:
    dbmfile = str(sys.argv[1])
    csvfile = str(sys.argv[2])

    dbm = anydbm.open(dbmfile,'c')

    file = open(csvfile, "r")
    print "saving the following key,value pairs\n"
    for line in file:
        result = re.search(r'([^\,]+),([^\n]*)\n', str(line))
        key = ''
        value = ''
        if result:
            key = str(result.group(1))
            value = str(result.group(2))
            print str(key) + ',' + str(value) + "\n"
            dbm[key] = value;


    dbm.close()
except:
    print "This tool loads your settings stored in CSV format to the DBM file.\nUsage:\n"
    print "python dbm_import_csv.py <dbm_file.db> <settings.csv>"
