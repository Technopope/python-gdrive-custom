#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import re
import os
import anydbm

from optparse import OptionParser

parser = OptionParser("%prog [option] <key> <value>") 

parser.add_option("-a", "--add", dest="add", help="Add Settings", nargs=2) 
parser.add_option("-c", "--change", dest="change", help="Change Settings", nargs=2)          
parser.add_option("-s", "--show", dest="show", help="Display Settings", action='store_true')          
parser.add_option("-i", "--import", dest="imp", help="Import Settings")
parser.add_option("-r", "--remove", dest="remove", help="Remove Settings")
parser.add_option("-d", "--dbase", dest="database", help="change database", default="gdrive.db")

(options, args) = parser.parse_args()

dbmfile = options.database

class dbfile():
    
    def __init__(self, database, mode):
        self.dbm = anydbm.open(database, mode)
    
    def get(self, key):   
        if key in self.dbm:
            return self.dbm[key]
        else:
            return False
            
    def set(self, key, value):
        self.dbm[key] = value
    
    def close(self):
        self.dbm.close()
    
    def delete(self, key):
        found = False
        if key in self.dbm:
            print "Deleted key: \"" + key + "\" with value: \"" + self.dbm[key] + "\""
            del self.dbm[key]
            found = True
        if not found:
            print "Key: \"" + key + "\" not found."
            
    def display(self):
        print '{:_^27} > {:_^25}'.format('KEY', 'VALUE')
        print "\n"
        for key in self.dbm.keys():
#            print key + " " + self.dbm[key]
            print '{:27} > {:>25}'.format(key, self.dbm[key])

if options.add:
    
    try:
    
        key = options.add[0]
        value = options.add[1]
    
        add = dbfile(dbmfile, 'c')
        
        if add.get(key) == False:
            add.set(key,value)
            print "added key: \"" +  key + "\" with value: \"" + add.get(key) + "\""
        else:
            print "Key already exists"
    
        add.close()
    
    except:
        
        print "Usage: " + __file__ + " -a or --add <key> <value> (-d database.db else gdrive.db is used)"
        print "If you want to change a value use -c/--change instead"

elif options.change:
    
    try:
        
        key = options.change[0]
        value = options.change[1]
    
        change = dbfile(dbmfile, 'w')
        if change.get(key) != False:
            old_value = change.get(key)
            change.set(key,value)
            print "Changed \"" + key + "\" from \"" + old_value + "\" to \"" + change.get(key) + "\""
        else:
            print "Key \"" + key + "\" can not be changed, because he doesn't exist in database"
        
        change.close()

    except:
        
        print "Usage: " + __file__ + " -c or --change <key> <value> (-d database.db else gdrive.db is used)"
        print "If you want to add a value use -a/--add instead"
        
elif options.show:
    
    try:
        
        show = dbfile(dbmfile, 'r')
        show.display()
        show.close()
    
    except:
        
        print "Usage: " + __file__ + " -s (-d database.db else gdrive.db is used)"
    

elif options.imp:
    
    try:
        
        imp = dbfile(dbmfile, 'c')
        
        regexp = r'\<setting id\=\"([^\"]+)\" value\=\"([^\"]+)" \/\>'
        
        if os.path.splitext(os.path.basename(options.imp))[1] == '.csv':
           regexp = r'([^\,]+),([^\n]+)\n'
        
        file = open(options.imp, "r")
        print "saving the following key,value pairs\n"
        for line in file:
            result = re.search(regexp, str(line))
            key = ''
            value = ''
            if result:
                key = str(result.group(1))
                value = str(result.group(2))
                print str(key) + ',' + str(value) + "\n"
                imp.set(key, value);
    
        imp.close()
    
    except:
        
        print "Usage: " + __file__ + " -i settings.xml (-d database.db else gdrive.db is used)"
        
elif options.remove:
    
    try:
        
        remove = dbfile(dbmfile, 'w')
        remove.delete(options.remove)
        remove.close()
    
    except:
        
        print "Usage: " + __file__ + " -r <key> (-d database.db else gdrive.db is used)"
else:
    
    parser.print_help()
