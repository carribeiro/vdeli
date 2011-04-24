LOCAL_SETTINGS = True
from settings import *
DEBUG = True

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)
INSTALLED_APPS += ('debug_toolbar', )

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS' : False,
}

CACHE_BACKEND = 'dummy://'

DATABASES = {
    'default': {
        'NAME': 'cdn',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'cdnmanager',
        'PASSWORD': 'CdnManager',
        'HOST': 'localhost',
    },
}


import logging
logging.basicConfig(filename=rel('log.txt'),
                    level=logging.INFO,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
