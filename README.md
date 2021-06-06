# Python-GoogleDrive-VideoStream

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d2f3f5f294c4e0db6112cfb4c2ba3d8)](https://www.codacy.com/app/ddurdle/Python-GoogleDrive-VideoStream?utm_source=github.com&utm_medium=referral&utm_content=ddurdle/Python-GoogleDrive-VideoStream&utm_campaign=badger)


This package replaces GoogleDrive-VideoStream (which was written in PHP).

This plugin is a direct port of Google Drive plugin for KODI.  The purpose of this plugin is to service content delivered in Google Drive plugin for KODI through any HTML5 client.

Use cases:
- export-and-import of STRM files for playback in Emby-Server
- playback of media through Safari and Chrome on iOS (iphone, ipod touch, ipad)
- playback of media through Firefox and Chrome on Android devices (tv players, phone, tablets)
- playback of media through any web browser on Windows, Mac OS, Linux
- playback of media through media player (such as VLC, KODI) that supports HTTPS streams

Current status - alpha testing.

Current status of items:
- support for encfs (planned)
- SRT / CC (planning stage)
- cache and offline playback (planning stage)



Python 2 is required.

For a docker version, see:
https://hub.docker.com/r/rxwatcher/pgdvs-docker
http://hub.docker.com/r/mrmachine/python-googledrive-videostream
https://github.com/choldi/docker-pythongdv


To start the scheduler only, run:

python scheduler.py

The default dbmfile is ./gdrive.db and the default port to run on is 9988.  You can override these by running:

python scheduler.py <dbmfile> <port>


To start the media server with no scheduler, run:

python noscheduler.py

The default dbmfile is ./gdrive.db and the default port to run on is 9988.  You can override these by running:

python noscheduler.py <dbmfile> <port>


To start the media server with scheduler, run:

python default.py

The default dbmfile is ./gdrive.db and the default port to run on is 9988.  You can override these by running:

python default.py <dbmfile> <port>

To use SSL using a SSL certificate (.pem file) you provide, change the port parameter (if required) and provide a third argument of the .pem file

python default.py <dbmfile> <port> <ssl certfile>

example:

python default.py ./gdrive.db 443 ./mycert.pem


You can use the setting.xml from either gdrive or gdrive-testing plugin for KODI.  You can import this using setup.py.  This is not required as you can setup the instance using the settings pane within the web interface.

A NOTE ABOUT STRM FILES:

You can import STRM files from a KODI install, but you will need to update the URL in them to resolve to the VideoStream:

A perl script that recursively updates files in a directory which has contents matched to a specified string, updating the match with a replacement can be found here:
https://github.com/ddurdle/PERL-Misc_Scripts/blob/master/grep/recursive_replace.pl

You can run it such as:
perl recursive_replace.pl -d directory_with_path -g "plugin://plugin.video.gdrive/" -r "http://localhost:9988/default"

which will navigate through "directory_with_path" looking for files with contents "plugin://plugin.video.gdrive/" and replacing it with "http://localhost:9988/default".  This would change the STRM files to resolve to an install of VideoStream running on localhost port 9988.  You can replace this with whatever applies to your situation.

You can always re-generate the STRM files using VideoStream using the web interface.  When doing such, you have the option to override the protocol (http://), hostname and port.