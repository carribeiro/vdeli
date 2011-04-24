#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__autor__ = "Thales Chácara <chacara@gmail.com>"
__date__ = "16/04/2011 16:50"

"""
description:

    a simple testing tool, just to send files for the 
    ftpserver automatically. ftpput uses the module ftputil, 
    is a high level interface to the module ftplib. 
"""

import ftputil, os, sys, getopt

def usage():
    """    
    prints help message and explain details of the parameters.    
    """
    
    try:
        print '''usage: ftpput.py -s <hostname> -u <username> -p <passwd> -l <video-file> -t <target-dir> \n
arguments:
        -s, --server      (hostname or ip address)
        -u, --user        (username)
        -p, --passwd      (password)
        -l, --video-file  (local video file)
        -t, --target-dir  (put video file in remote directory)

special modes:
            -a (change transfer mode to ascii (default = binary))
            -o (overwrite video file if exists)
        
Video Delivery Network <http://www.vdeli.com.br>'''
    except:
        return 0

def put(hostname, username, passwd, local, target, mode, overwrite):
    """    
    performs upload videos to FTP server.
    
    return:
        0 - operation completed.
        1 - could not establish connection with server.
        2 - video has not been sent.
    """

    try:
        ftp = ftputil.FTPHost(hostname, username, passwd) 
    except: 
        return 1

    try:
        ftp.makedirs(target, mode=None)
        
        video = local.split('/')[-1]
        target = target + '/' + video
                
        if not ftp.path.exists(target):
            ftp.upload(local, target, mode, callback=None)
        elif overwrite:
            ftp.upload(local, target, mode, callback=None)
    except:
        return 2
    
    return 0


def main(argv):
    """    
    provides support for parsing command line.
    """
    try: 
        opts, args = getopt.getopt(argv, "h:s:u:p:l:t:a:o", ["help",
                                                           "server",
                                                           "username",
                                                           "passwd",
                                                           "video-file",
                                                           "target-dir"
                                                           ]
                                   )
    except getopt.GetoptError, error:
        print str(error)
        usage()
        sys.exit(2)
    
    # (default transfer mode: binary)
    mode = "b"
    overwrite = False
    
    for option, argument in opts:
        if option == "-a":
            mode = "a"
        elif option == "-o":
            overwrite = True         
        elif option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-s", "--server"):
            hostname = argument
        elif option in ("-u", "--username"):
            username = argument
        elif option in ("-p", "--passwd"):
            passwd = argument
        elif option in ("-l", "--video-file"):
            local = argument
        elif option in ("-t", "--target-dir"):
            target = argument
        else:
            assert False, "unhandled option"

    try:
        putout = put(hostname, username, passwd, local, target, mode, overwrite)
    except:
        usage()
        sys.exit()
    
    putmsg = ["operation completed.",
              "could not establish connection with server.",
              "video has not been sent."
              ]

    print putmsg[putout]

if __name__ == "__main__":
    main(sys.argv[1:])