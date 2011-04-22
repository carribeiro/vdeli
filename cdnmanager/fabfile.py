import os
from fabric.api import *
from fabric.contrib.files import exists
from contextlib import contextmanager as _contextmanager
from fabric.contrib.project import rsync_project
from fabric.context_managers import settings

# constants

DEFAULT_PATH_LOCALDEV = '/home/%(user)s/work'
DEFAULT_HOST_LOCALDEV = 'localhost'
DEFAULT_USER_LOCALDEV = env.user

DEFAULT_PATH_SERVER = '/srv/'
DEFAULT_HOST_SERVER = '187.1.90.3'
DEFAULT_USER_SERVER = 'vdeliadmin'

# globals

env.prj_name = 'vdeli' # no spaces!
env.webserver = 'apache2' # nginx or apache2 (directory name below /etc!)
env.dbserver = 'postgresql' # mysql or postgresql
env.user='vdeliadmin'

# environments
#
# the project can be deployed on two kinds of environment: the localhost is 
# for a local (development) deployment, and the cdnmanager is for a remote 
# server deployment. In both cases, we always set up a single host at a time.
# It does not make sense to deploy the cdnmanager on more than one host.

def localhost(path=DEFAULT_PATH_LOCALDEV, user=DEFAULT_USER_LOCALDEV, 
        host=DEFAULT_HOST_LOCALDEV, createdb=True):
    """ Prepares the local computer, assuming a development setup """
    env.hosts = [host] # always deploy to a single host
    env.user = user
    env.path = path % env  # any attribute in env can be used. we must check 
                           # whether this opens a security hole or not, 
                           # depending on what is in the env dictionary
    env.project_path = '%(path)s/%(prj_name)s' % env
    env.virtualenv_path = '%(project_path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.createdb = createdb

def cdnmanager(path=DEFAULT_PATH_SERVER, user=DEFAULT_USER_SERVER, host=DEFAULT_HOST_SERVER, 
        createdb=True):
    """ Deploy to a dedicated webserver (can be staging or production) """
    env.hosts = [host] # always deploy to a single host
    env.user = user
    env.path = path # do not perform path substitution on the server.
                           # it's not really needed and it is safer this way.
    env.project_path = '%(path)s/%(prj_name)s' % env
    env.virtualenv_path = '%(project_path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.createdb = createdb

@_contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield

def setup():
    """
    Prepare server for the project
    """

    sudo('apt-get update')
    sudo('apt-get install gcc python-all-dev libpq-dev git-core -y')
    
    if not exists('/usr/bin/virtualenv',use_sudo=True):
        sudo('apt-get install python-virtualenv -y')
    if not exists('/usr/bin/pip',use_sudo=True):
        sudo('apt-get install python-pip -y')

    if env.hosts[0] == 'localhost':
        pass
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

    if env.createdb:
        if not exists('/etc/postgresql',use_sudo=True):
            sudo('apt-get install -y postgresql')
        # creates the db user and the database, but doesn't stop on failure, 
        # because these may have been created before
        # TODO: test if the user was created before, and if the db exists, instead of ignoring the error
        with settings(warn_only=True):
            sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER ENCRYPTED PASSWORD E\'%s\'"' % ('cdnmanager', 'CdnManager'), user='postgres')
            sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
            'cdn', 'cdnmanager'), user='postgres')

def deploy():
    if env.hosts[0] == 'localhost':
        # create project dir
        if not exists(env.path):
            sudo('mkdir %s' % env.path,user=env.user)

        if not exists(os.path.join(env.path, 'vdeli')):
            local('cd %(path)s && git clone git@github.com:carribeiro/vdeli.git' % env)
        else:
            local('cd %(path)s && cd vdeli && git pull' % env)
        
        # create virtualenv
        with cd(env.project_path):
            sudo('virtualenv .env --no-site-packages',user=env.user)
        
        # install packages
        with virtualenv():
            sudo('pip install -r %(project_path)s/cdnmanager/requirements.txt' % env,user=env.user)
            sudo('pip install django-debug-toolbar' % env,user=env.user)
        
        run('cp %(project_path)s/cdnmanager/local_settings.py %(project_path)s/cdnmanager/cdnmanager/cdn/' % env)

    # deploy on a remote system
    else:
        # create project dir
        if not exists(env.path):
            sudo('mkdir %s' % env.path,user=env.user)
    
        # checks the project locally (on the computer that's running fabric), checks the
        # the repository locally, and then copy it via rsync.
        local('cd /tmp && git clone git@github.com:carribeiro/vdeli.git' % env)
        sudo('chown %(user)s:%(user)s %(path)s' % env)
        rsync_project(
                local_dir = '/tmp/vdeli',
                remote_dir = env.path,
                delete=True,
            )
        local('rm -fr /tmp/%(prj_name)s' % env)
        # create virtualenv
        with cd(env.project_path):
            sudo('virtualenv .env --no-site-packages',user=env.user)
        
        # install packages
        with virtualenv():
            sudo('pip install -r %(project_path)s/requirements.txt' % env,user=env.user)

def configure_ftpserver():
    """ Configure the ftpserver to run as a daemon """
    # TODO: create a symlink on /etc/init.d for the ftpserver daemon