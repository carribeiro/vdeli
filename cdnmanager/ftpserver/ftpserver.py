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
"""

from pyftpdlib import ftpserver
import sqlite3
import pypid

ftpserver_daemon = pypid.Daemon()

if __name__ == "__main__":
    ftpserver_daemon.args(stdout='/var/log/ftpserver.log', 
                          pidfile='/var/run/ftpserver.pid')
    def ftpserverd():
        authorizer = ftpserver.DummyAuthorizer()
   
        db = sqlite3.connect("/srv/git/vdeli/cdnmanager/ftpserver/ftpusers.db")
        cur = db.cursor()
        cur.execute('select * from users')
        
        for user in cur:
            authorizer.add_user(user[0], user[1], \
                                "/srv/git/vdeli/cdnmanager/ftpserver", perm="elradfmw")
        
        authorizer.add_anonymous("/")
        handler = ftpserver.FTPHandler
        handler.authorizer = authorizer
        address = ("0.0.0.0", 21)
        ftpd = ftpserver.FTPServer(address, handler)
        ftpd.serve_forever()
    
    ftpserverd()