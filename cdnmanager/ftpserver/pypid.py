# -*- encoding: utf8 -*-

__autor__ = "Thales Chácara <chacara@gmail.com>"
__date__ = "16/04/2011 16:11"

"""
description:
    pypid is a module which provides a simplified way to run python code
    following the specifications of the Linux daemon.

"""

import sys, os, time
from signal import SIGTERM

class Daemon:
    def forks(self, stdout='/dev/null', stderr=None, stdin='/dev/null', 
                  pidfile=None, msg='iniciando pid: %s'):

        # Do first fork.
        try:
            pid = os.fork()
            if pid > 0: sys.exit(0) # Exit first parent.
        except OSError, e:
            sys.stderr.write("fork #1 falhou: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # Decouple from parent environment.
        os.chdir("/")
        os.umask(0)
        os.setsid()
    
        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0: sys.exit(0) # Exit second parent.
        except OSError, e:
            sys.stderr.write("fork #2 falhou: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # Open file descriptors and print start message
        if not stderr: stderr = stdout
        si = file(stdin, 'r')
        so = file(stdout, 'a+')
        se = file(stderr, 'a+', 0)
        pid = str(os.getpid())
        sys.stderr.write("\n%s\n" % msg % pid)
        sys.stderr.flush()
        if pidfile: file(pidfile,'w+').write("%s\n" % pid)
        
        # Redirect standard file descriptors.
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def args(self, stdout='/dev/null', stderr=None, stdin='/dev/null', 
                  pidfile='pid.txt', msg='iniciando pid: %s' ):
        if len(sys.argv) > 1 or stderr == 'stop':
            action = sys.argv[1]
            try:
                pf  = file(pidfile,'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            if 'stop' == action or 'restart' == action:
                if not pid:
                    mess = "não é possível parar, '%s' não foi encontrado.\n"
                    sys.stderr.write(mess % pidfile)
                    sys.exit(1)
                try:
                    while 1:
                        os.kill(pid, SIGTERM)
                        time.sleep(1)
                except OSError, err:
                    err = str(err)
                    if err.find("No such process") > 0:
                        os.remove(pidfile)
                        if 'stop' == action:
                            sys.exit(0)
                            action = 'start'
                            pid = None
                        else:
                            print str(err)
                            sys.exit(1)
            if 'status' == action:
                if not pid:
                    mess = "o processo se encontra parado.\n"
                    sys.stdout.write(mess)
                    sys.exit(1)
                if pid:
                    mess = "o processo '%s', esta sendo executado. \n"
                    sys.stdout.write(mess % pid)
                    sys.exit(1)
                       
            if 'start' == action:
                if pid:
                    mess = "inicialização abortada, '%s' já existe.\n"
                    sys.stderr.write(mess % pidfile)
                    sys.exit(1)
                self.forks(stdout, stderr, stdin, pidfile, msg)
                return
        print "uso: %s {start|stop|restart|status}" % sys.argv[0]
        sys.exit(2)
    
