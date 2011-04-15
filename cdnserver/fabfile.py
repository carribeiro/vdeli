import os
from fabric.api import *
from fabric.operations import put




env.hosts = ['deploy@10.7.1.5']
env.deploy_user = 'deploy'

def install_nginx(server_name, server_ip,document_root='/data',\
                  install_nginx='True'):
    '''
    Use this function to install and configure nginx on a remote system
    @param server_name: server name (needs for nginx configuration)
    @param server_ip: ip address of the server
    @param document_root: document root for serving files
    
    Example of usage:
    fab install_nginx:server_name='test.host.br',server_ip='10.7.1.5',hosts="deploy@10.7.1.5"
    
    '''
    # Install nginx
    if install_nginx == 'True':
        sudo('apt-get install nginx -y')
    
    # Create nginx cfg
    cfg = open('cbn', 'w')
    cfg_data = """server {
    listen   %s:80 ;
    server_name %s;

    access_log  /var/log/nginx/%s.access.log;

    location / {
        root   %s;
        index  index.html index.htm;
    }
}""" % (server_ip,server_name,server_name,document_root)
    cfg.write(cfg_data)
    cfg.close()
    put('cbn','/etc/nginx/sites-available',use_sudo=True,mode=0644)
    # Create symlink
    sudo('ln -s /etc/nginx/sites-available/cbn /etc/nginx/sites-enabled/cbn')
    # Set owner
    sudo('chown www-data:www-data /etc/nginx/sites-available/cbn')
    # Start nginx
    sudo('/etc/init.d/nginx start')