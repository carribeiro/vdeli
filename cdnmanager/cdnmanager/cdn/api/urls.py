from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import NoAuthentication
from api.handlers import TransferStatHandler

no_auth = NoAuthentication()

transferstat_handler = Resource(TransferStatHandler, authentication=no_auth)

urlpatterns = patterns('',
   url(r'^queue/(?P<queue_id>\d+)/$', transferstat_handler, {'emitter_format': 'json'}, name='trasnfer_status_queue'),
)
