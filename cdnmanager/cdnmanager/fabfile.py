import os
from fabric.api import *
from fabric.contrib.files import exist



def install_prerequirements():
    '''
    Install virtualenv and pip
    '''
    if not exists('/usr/bin/virtualenv',use_sudo=True):
        sudo('apt-get install python-virtualenv -y')
    if not exists('/usr/bin/pip',use_sudo=True):
        sudo('apt-get install python-pip -y')

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