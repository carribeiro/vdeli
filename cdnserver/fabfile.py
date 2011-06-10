from fabric.state import env
from cuisine import *




DEFAULT_PATH = '/srv'

#env.user = 'vdeliadmin'
env.prj_name = 'vdeli' # no spaces!

def variables(user=None, path=DEFAULT_PATH):
    if user:
        env.user = user
    else:
        env.user = 'vdeliadmin'
    env.path = path % env  # allows substitution of the %(env.user)s attribute. 
                           # however any attribute in env can be used. we must
                           # check whether this opens a security hole or not, 
                           # depending on what is in the env dictionary
    env.project_path = '%(path)s/%(prj_name)s' % env

def test():
    h = run('hostname')
    d = run('domainname')
    if d != '(none)':
        servername = '%s.%s' % (h,d)
    else:
        servername = h
    print servername

def update_logrotate(text):
    res = []
    for line in text.split('\n'):
        if line.strip().startswith('/var/log/nginx/*.log {'):
            res.append('/var/log/nginx/*.log {\n\tdateext')
        # We don't want to wait next rotation. Compress all files
        elif line.strip().startswith('delaycompress'):
            pass
        else:
            res.append(line)
    return '\n'.join(res)

def install_nginx():
    package_ensure('nginx')
    # Prepare a servername
    h = run('hostname')
    d = run('domainname')
    if d != '(none)':
        servername = '%s.%s' % (h,d)
    else:
        servername = h

    # Create nginx conf
    conf = text_template(text_strip_margin(
        """
        |server {
        |    listen ${HOST}:80 ;
        |    server_name ${SERVER_NAME};
        |    access_log  /var/log/nginx/${SERVER_NAME}.access.log;
        |
        |    location / {
        |        root   ${PROJECT_PATH}/cdnserver/data;
        |        index  index.html index.htm;
        |    }
        |}
        """
        ), dict(
            HOST=env.host_string,
            SERVER_NAME=servername,
            PROJECT_PATH=env.project_path
            )
    )
    mode_sudo()
    file_write('/etc/nginx/sites-available/cdn',
               conf,
               mode='644',
               owner='www-data',
               group='www-data'
    )

    run('ln -s /etc/nginx/sites-available/cdn /etc/nginx/sites-enabled/cdn')

    mode_sudo()
    # Changing logrotate.d/nginx
    file_update(
        '/etc/logrotate.d/nginx',
        update_logrotate
    )
    
    # Run nginx
    run('service nginx start')

def create_user():
    mode_sudo()
    user_ensure('vdeliadmin', passwd='vDe11Admin')
