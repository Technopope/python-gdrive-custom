#!/bin/sh

NAME=Python-GDrive-Videostream
PIDFILE=$PWD/$NAME.pid
LOGFILE=$PWD/logs/$NAME.log
COMMAND="/usr/bin/python2 ${PWD}/default.py"

start() {
    if [ -e $PIDFILE ]; then
        printf "\n${NAME} already running with PID $(cat $PIDFILE).\n"
        exit
    fi
    if [ ! -d $PWD/logs ]
        then mkdir $PWD/logs
    fi
    if [ -e $LOGFILE ]; then
        if [ -e $LOGFILE.bck ]
            then rm $LOGFILE.bck
        fi
        mv $LOGFILE $LOGFILE.bck
    fi
    exec $COMMAND > $LOGFILE 2> $LOGFILE.error & echo $! > $PIDFILE
}

stop() {
    if [ -e $PIDFILE ]; then 
        PID=$(cat $PIDFILE)
        printf "\n$PID\n"
        kill $PID
        rm $PIDFILE
    else
        printf "\nNo running Instance for ${NAME} found.\n"
        exit
    fi
 
}

case $1 in
    start)
    printf "Starting: $NAME\n"
    start
    ;;
    stop)
    printf "Stopping: $NAME\n"
    stop
    ;;
    restart)
    printf "Restarting: $NAME\n"
    stop
    sleep 1
    start
    ;;
    *)
    echo "usage: $NAME.sh {start|stop|restart}"
    exit 1
    ;;
esac

exit 0
