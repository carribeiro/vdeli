#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from sqlite3.test.userfunctions import authorizer_cb

__autor__ = "chácara"

from pyftpdlib import ftpserver
import sqlite3

authorizer = ftpserver.DummyAuthorizer()

db = sqlite3.connect('ftpusers.db')
cur = db.cursor()
cur.execute('select * from users')

for user in cur:
    authorizer.add_user(user[0], user[1], "/srv/git/vdeli/ftpd", perm="elradfmw")

authorizer.add_anonymous("/")
handler = ftpserver.FTPHandler
handler.authorizer = authorizer
address = ("0.0.0.0", 21)
ftpd = ftpserver.FTPServer(address, handler)
ftpd.serve_forever()
