#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Init file for ftpserver server daemon
#
# chkconfig: 2345 99 99
# description: ftpserver initialization to system structure based on redhat

__autor__ = "Thales Chácara <chacara@gmail.com>"
__date__ = "16/04/2011 16:11"

"""
description:

    this is a simple FTP server based on pyftpdlib, which is a great library
    that supports almost everything you need for a working FTP. It checks the 
    user authorization in a user library stored in a database, that is managed
    by the cdnmanager component.
    
deploy:
    
    create a symlink to this file in /etc/init.d/,
    do not forget set execute permissions for that symlink.
"""

from pyftpdlib import ftpserver
from vdeliauthorizer import SQLite3Authorizer
import sqlite3, time, pypid

now = lambda: time.strftime("[%Y-%b-%d %H:%M:%S]")
f1 = open('ftpd.log', 'a')
f2 = open('ftpd.lines.log', 'a')
f3 = open('ftpd.errlog', 'a')

def standard_logger(msg):
    f1.write("%s %s\n" %(now(), msg))
    f1.flush()

def line_logger(msg):
    f2.write("%s %s\n" %(now(), msg))
    f2.flush()

def errlog(msg):
    f3.write("%s %s\n" %(now(), msg))
    f3.flush()

def ftpserverd():
    ftpserver.log = standard_logger
    ftpserver.logline = line_logger
    authorizer = SQLite3Authorizer()
    handler = ftpserver.FTPHandler
    handler.authorizer = authorizer
    address = ('', 21)
    server = ftpserver.FTPServer(address, handler)
    server.serve_forever()
    

if __name__ == "__main__":
    ftpserver_daemon = pypid.Daemon()
    ftpserver_daemon.args(stdout='/var/log/ftpserver.log', 
                          pidfile='/var/run/ftpserver.pid')
    ftpserverd()