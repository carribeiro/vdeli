import os
from fabric.api import *
from fabric.contrib.files import exists
from contextlib import contextmanager as _contextmanager
from fabric.contrib.project import rsync_project

# globals
env.prj_name = 'vdeli' # no spaces!
env.webserver = 'apache2' # nginx or apache2 (directory name below /etc!)
env.dbserver = 'postgresql' # mysql or postgresql

# environments

def localhost(path='/home/%(user)s/PROJECTS' % env,user='vdeliadmin',\
              createdb=True):
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = user
    env.path = path
    env.project_path = '%(path)s/%(prj_name)s' % env
    env.virtualenv_path = '%(project_path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.createdb = createdb

def cdnmanager(path='/srv',user='vdeliadmin',createdb=True):
    "Use the actual webserver"
    env.hosts = ['187.1.90.3'] # Change to your server name!
    env.user = user
    env.path = path
    env.project_path = '%(path)s/%(prj_name)s' % env
    env.virtualenv_path = '%(project_path)s/.env' % env
    env.activate = 'source %(virtualenv_path)s/bin/activate' % env
    env.createdb = createdb

def test(path='/srv',user='vdeliadmin',createdb=True):
    "Use the actual webserver"
    env.hosts = ['10.7.1.5'] # Change to your server name!
    env.user = user
    env.path = path
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
        sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER ENCRYPTED PASSWORD E\'%s\'"' % ('cdnmanager', 'CdnManager'), user='postgres')
        sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
            'cdn', 'cdnmanager'), user='postgres')

def deploy():
    if env.hosts[0] == 'localhost':
        # create project dir
        if not exists(env.path):
            sudo('mkdir %s' % env.path,user=env.user)
    
        local('cd %(path)s && git clone git@github.com:carribeiro/vdeli.git' % env)
        
        # create virtualenv
        with cd(env.project_path):
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
        
        put('requirements.txt',env.project_path,use_sudo=True)
        
        with virtualenv():
            sudo('pip install -r %(project_path)s/requirements.txt' % env,user=env.user)
        # setting up local_settings
        local_settings = open('local_settings.py', 'w')
        local_settings_data = """
LOCAL_SETTINGS = True
from settings import *
DEBUG = True

CACHE_BACKEND = 'dummy://'

DATABASES = {
    'default': {
        'NAME': 'cdn',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'cdnmanager',
        'PASSWORD': 'CdnManager',
    },
}


import logging
logging.basicConfig(filename=rel('log.txt'),
                    level=logging.INFO,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
"""
        local_settings.write(requirements_data)
        local_settings.close()
        
        put('local_settings.py','%(project_path)s/cdnmanager/cdnmanager/cdn/' % env,
            use_sudo=True)

    # deploy on a remote system
    else:
        # create project dir
        if not exists(env.path):
            sudo('mkdir %s' % env.path,user=env.user)
    
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
        requirements = open('requirements.txt', 'w')
        requirements_data = """Django
    South
    django-extensions
    pyftpdlib
    psycopg2
    """
        requirements.write(requirements_data)
        requirements.close()
        
        put('requirements.txt',env.project_path,use_sudo=True)
        
        with virtualenv():
            sudo('pip install -r %(project_path)s/requirements.txt' % env,user=env.user)

