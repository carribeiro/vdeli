import os
from fabric.api import *
from fabric.contrib.files import exists
from contextlib import contextmanager as _contextmanager

# globals
env.prj_name = 'vdeli' # no spaces!
env.webserver = 'apache2' # nginx or apache2 (directory name below /etc!)
env.dbserver = 'postgresql' # mysql or postgresql

# environments

def localhost(path='/home/%(user)s/PROJECTS' % env,user='vdeliadmin'):
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = user
    env.path = '%s/%s' % (path,env.prj_name)
    env.virtualenv_path = '%(path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.use_local_devel_machine = True

def cdnmanager():
    "Use the actual webserver"
    env.hosts = ['187.1.90.3'] # Change to your server name!
    env.user = 'vdeliadmin'
    env.path = '/srv/%(prj_name)s' % env
    env.virtualhost_path = '%s/virtualenv/vdeli' % env.path
    env.pysp = '%(virtualhost_path)s/lib/python2.6/site-packages' % env
    env.tmppath = '/var/tmp/django_cache/%(prj_name)s' % env

def test(path='/home/%(user)s/PROJECTS' % env,user='vdeliadmin'):
    "Test server"
    env.hosts = ['10.7.1.5'] # Change to your server name!
    env.user = user
    env.path = '%s/%s' % (path,env.prj_name)
    env.virtualenv_path = '%(path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.use_local_devel_machine = True

@_contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment

    copied from: https://github.com/fiee/generic_django_project/blob/master/fabfile.py
    """
    
    # for localhost we don't need the webserver
    if env.use_local_devel_machine:
        
        sudo('apt-get install gcc python-all-dev libpq-dev git-core -y')
        
        if not exists('/usr/bin/virtualenv',use_sudo=True):
            sudo('apt-get install python-virtualenv -y')
        if not exists('/usr/bin/pip',use_sudo=True):
            sudo('apt-get install python-pip -y')
        
        # create project dir
        if not exists(env.path):
            sudo('mkdir %s' % env.path,user=env.user)
        # create virtualenv
        with cd(env.path):
            sudo('virtualenv .env --no-site-packages',user=env.user)
        
        # install packages
        requirements = open('requirements.txt', 'w')
        requirements_data = """Django
South
django-extensions
pyftpdlib
psycopg2
"""
        requirements.write(requirements_data)
        requirements.close()
        
        put('requirements.txt',env.path,use_sudo=True)
        
        with virtualenv():
            sudo('pip install -r %(path)s/requirements.txt' % env,user=env.user)

        sudo('apt-get install -y postgresql')
        sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER ENCRYPTED PASSWORD E\'%s\'"' % ('cdnmanager', 'CdnManager'), user='postgres')
        sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
            'cdn', 'cdnmanager'), user='postgres')
        
#        with cd(env.path):
#            sudo('git clone git@github.com:carribeiro/vdeli.git')

    else:
        # install webserver and database server
        sudo('apt-get remove -y apache2 apache2-mpm-prefork apache2-utils') # is mostly pre-installed
        # install gcc C compiler
        sudo('apt-get install gcc -y')
        if env.webserver=='nginx':
            sudo('apt-get install -y nginx')
        else:
            sudo('apt-get install -y apache2-mpm-worker apache2-utils') # apache2-threaded
            sudo('apt-get install -y libapache2-mod-wsgi') # outdated on hardy!

        sudo('apt-get install -y postgresql git git-core')
        sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER ENCRYPTED PASSWORD E\'%s\'"' % ('cdnmanager', 'CdnManager'), user='postgres')
        sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
            'cdn', 'cdnmanager'), user='postgres')

