from django.conf import settings
from piston.handler import BaseHandler, rc
from videorepo.models import TransferQueue



class TransferStatHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = TransferQueue

    def read(self, request, queue_id):
        try:
            queue = TransferQueue.objects.get(id=queue_id)
        except TransferQueue.DoesNotExist:
            return rc.NOT_FOUND

        return queue
