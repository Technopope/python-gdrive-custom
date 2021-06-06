
import sys
import re
import os

print "hello world"


# global variables
import addon_parameters
addon = addon_parameters.addon
cloudservice3 = addon_parameters.cloudservice3
cloudservice2 = addon_parameters.cloudservice2

from resources.lib import cloudservice
from resources.lib import gdrive_api2

try:

    remote_debugger = 'true'#settings.getSetting('remote_debugger')
    remote_debugger_host = 'localhost'#settings.getSetting('remote_debugger_host')

    # append pydev remote debugger
    if remote_debugger == 'true':
        # Make pydev debugger works for auto reload.
        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
        import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace(remote_debugger_host, stdoutToServer=True, stderrToServer=True)
except ImportError:
    xbmc.log(addon.getLocalizedString(30016), xbmc.LOGERROR)
    sys.exit(1)
except :
    pass

#try:
cloudservice = cloudservice2(None,addon,str(sys.argv[2]),'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.38 Safari/532.0',None, DBM=str(sys.argv[1]))
#except:
#    print "Usage: python gdServer.py DBM instancename\nexample: python gdServer.py gdrive.db username\n"
