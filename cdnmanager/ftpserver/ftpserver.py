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
from vdeliauthorizer import DjangoAuthorizer
import time
import pypid
import sys

try:
    import ftpconfig
except:
    FTP_HOME_DIR = "/srv/uploads"

now = lambda: time.strftime("[%Y-%b-%d %H:%M:%S]")

class FTPServer:
    """ Simple class that encapsulates a ftpserver and adds custom logging.
    """

    def __init__(self, log_name='/var/log/ftpserver.log'):
        if log_name == '':
            self.log = sys.stdout
        else:
            self.log = open(log_name, 'a')

    def standard_logger(self, msg):
        self.log.write("%s %s\n" %(now(), msg))
        self.log.flush()

    def line_logger(self, msg):
        self.log.write("%s %s\n" %(now(), msg))
        self.log.flush()

    def error_loggger(self, msg):
        self.log.write("%s %s\n" %(now(), msg))
        self.log.flush()

    def ftpserverd(self):
        ftpserver.log = self.standard_logger
        ftpserver.logline = self.line_logger
        ftpserver.logerror = self.error_loggger
        authorizer = DjangoAuthorizer()
        handler = ftpserver.FTPHandler
        handler.authorizer = authorizer
        address = ('', 21)
        server = ftpserver.FTPServer(address, handler)
        server.serve_forever()

if __name__ == "__main__":
    if "--debug" in sys.argv:
        FTPServer(log_name='').ftpserverd()
    else:
        ftpserver_daemon = pypid.Daemon()
        ftpserver_daemon.args(stdout='/var/log/ftpserver.log', 
                              pidfile='/var/run/ftpserver.pid')
        FTPServer().ftpserverd()
