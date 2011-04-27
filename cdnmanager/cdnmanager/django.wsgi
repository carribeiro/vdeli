import sys
import site
import os

vepath = '/srv/vdeli/.env/lib/python2.6/site-packages'

prev_sys_path = list(sys.path)
# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)
# add the app's directory to the PYTHONPATH
sys.path.append('/srv/vdeli/cdnmanager/cdnmanager')
sys.path.append('/srv/vdeli/cdnmanager/cdnmanager/cdn')

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

# import from down here to pull in possible virtualenv django install
from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'cdn.settings'
application = WSGIHandler()
