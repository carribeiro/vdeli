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
    print '''usage: ftpput.py -s <hostname> -u <user> -p <passwd> -l <video-file> -t <target-dir> \n
arguments:
        -s, --server      (hostname or ip address)
        -u, --user        (username)
        -p, --passwd      (password)
        -l, --video-file  (local video file)
        -t, --target-dir  (put video file in remote directory)
        
Video Delivery Network <http://www.vdeli.com.br>'''

def put(hostname, username, passwd, local, target, mode):
    """    
    performs upload videos to FTP server.
    
    return:
        0 - upload completed.
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
        ftp.upload(local, target, mode, callback=None)
    except:
        return 2
    
    return 0


def main(argv):
    """    
    provides support for parsing command line.
    
    return:
        0 - upload completed.
        1 - could not establish connection with server.
        2 - video has not been sent.
    """
    try: 
        opts, args = getopt.getopt(argv, "h:s:u:p:l:t:a", ["help",
                                                           "server",
                                                           "username",
                                                           "passwd",
                                                           "video-file",
                                                           "target-dir"]
                                   )
    except getopt.GetoptError, error:
        print str(error)
        usage()
        sys.exit(2)
    
    # (default transfer mode: binary)
    mode = "b"
    
    for option, argument in opts:
        if option == "-a":
            mode = "a"
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

    output = put(hostname, username, passwd, local, target, mode)
    
    messages = ["upload completed.",
                "could not establish connection with server.",
                "video has not been sent."
                ]
    print messages[output]


if __name__ == "__main__":
    main(sys.argv[1:])