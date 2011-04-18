import os
from fabric.api import *
from fabric.contrib.files import exists

# globals
env.prj_name = 'vdeli' # no spaces!
env.use_photologue = False # django-photologue gallery module
env.use_feincms = True
env.use_medialibrary = True # feincms.medialibrary or similar
env.use_daemontools = False
env.use_supervisor = True
env.use_celery = False
env.webserver = 'nginx' # nginx or apache2 (directory name below /etc!)
env.dbserver = 'mysql' # mysql or postgresql

# environments

def localhost():
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = 'vdeliadmin'
    env.path = '/home/%(user)s/work/%(prj_name)s' % env
    env.virtualhost_path = '%s/virtualenv/vdeli' % env.path
    env.pysp = '%(virtualhost_path)s/lib/python2.6/site-packages' % env
    env.tmppath = '/var/tmp/django_cache/%(prj_name)s' % env

def cdnmanager():
    "Use the actual webserver"
    env.hosts = ['187.1.90.3'] # Change to your server name!
    env.user = 'vdeliadmin'
    env.path = '/srv/%(prj_name)s' % env
    env.virtualhost_path = '%s/virtualenv/vdeli' % env.path
    env.pysp = '%(virtualhost_path)s/lib/python2.6/site-packages' % env
    env.tmppath = '/var/tmp/django_cache/%(prj_name)s' % env

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment

    copied from: https://github.com/fiee/generic_django_project/blob/master/fabfile.py
    """
    require('hosts', provided_by=[localhost,cdnmanager])
    require('path')
    # install Python environment
    sudo('apt-get install -y build-essential python-dev python-setuptools python-imaging python-virtualenv python-yaml')
    # install some version control systems, since we need Django modules in development
    sudo('apt-get install -y git-core') # subversion git-core mercurial
        
    # install more Python stuff
    # Don't install setuptools or virtualenv on Ubuntu with easy_install or pip! Only Ubuntu packages work!
    sudo('easy_install pip')

    if env.use_daemontools:
        sudo('apt-get install -y daemontools daemontools-run')
        sudo('mkdir -p /etc/service/%(prj_name)s' % env, pty=True)
    if env.use_supervisor:
        sudo('pip install supervisor')
        sudo('echo; if [ ! -f /etc/supervisord.conf ]; then echo_supervisord_conf > /etc/supervisord.conf; fi', pty=True) # configure that!
        sudo('echo; if [ ! -d /etc/supervisor ]; then mkdir /etc/supervisor; fi', pty=True)
    if env.use_celery:
        sudo('apt-get install -y rabbitmq-server') # needs additional deb-repository!
        if env.use_daemontools:
            sudo('mkdir -p /etc/service/%(prj_name)s-celery' % env, pty=True)
        # for supervisor, put celery's "program" block into supervisor.ini!
    
    # install webserver and database server
    sudo('apt-get remove -y apache2 apache2-mpm-prefork apache2-utils') # is mostly pre-installed
    if env.webserver=='nginx':
        sudo('apt-get install -y nginx')
    else:
        sudo('apt-get install -y apache2-mpm-worker apache2-utils') # apache2-threaded
        sudo('apt-get install -y libapache2-mod-wsgi') # outdated on hardy!
    if env.dbserver=='mysql':
        sudo('apt-get install -y mysql-server python-mysqldb')
    elif env.dbserver=='postgresql':
        sudo('apt-get install -y postgresql python-psycopg2')

def install_prerequirements():
    '''
    Install virtualenv and pip
    '''
    if not exists('/usr/bin/virtualenv',use_sudo=True):
        sudo('apt-get install python-virtualenv -y')
    if not exists('/usr/bin/pip',use_sudo=True):
        sudo('apt-get install python-pip -y')

def mk_data_dir():
    if not exists('/data',use_sudo=True):
        sudo('mkdir /data')

def create_virtual_env(virtual_env_path='/data',virtual_env_name='cdnmanager'):
    '''
    Create virtualenv
    @param virtual_env_path: path to the virtualenv
    @param virtual_env_name: virtualenv name
    '''
    env_path = os.path.join(virtual_env_path,virtual_env_name)
    with cd(virtual_env_path):
        sudo('virtualenv %s --no-site-packages' % virtual_env_name)

def activate_env(virtual_env_path='/data',virtual_env_name='cdnmanager'):
    '''
    Activate virtualenv
    @param virtual_env_path: path to the virtualenv
    @param virtual_env_name: virtualenv name
    '''
    return 'source %s/%s/bin/activate' % (virtual_env_path, virtual_env_name)

def virtualenv(command,virtual_env_path='/data',virtual_env_name='cdnmanager',
               user=None):
    '''
    Run command for specific virtualenv
    @param command: a command
    @param virtual_env_path: path to the virtualenv
    @param virtual_env_name: virtualenv name
    @param user: deploy user
    '''
    with cd(os.path.join(project_dir(project_name), 'm2c')):
        if user is None:
            sudo(activate_env(project_name, env_name) + ' && ' + command)
        else:
            sudo(activate_env(project_name, env_name) + ' && ' + command, user=user)
            


def bootstrap():
    install_prerequirements()
    mk_data_dir()
