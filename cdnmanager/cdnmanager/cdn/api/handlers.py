from django.conf import settings
from piston.handler import BaseHandler, rc
from videorepo.models import TransferQueue
from django.core.paginator import Paginator, EmptyPage, InvalidPage



class TransferStatHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id', 'transfer_status', 'percentage_transferred')
    model = TransferQueue

    def read(self, request, queue_id=None):
        if queue_id:
            try:
                queue = TransferQueue.objects.get(id=queue_id)
            except TransferQueue.DoesNotExist:
                return rc.NOT_FOUND

            return queue
        else:
            try:
                page = int(request.GET.get('page', 1))
            except ValueError:
                page = 1

            queue_list = TransferQueue.objects.all()
            p = Paginator(queue_list, 10)

            try:
                page = int(request.GET.get('page', 1))
            except ValueError:
                page = 1

            try:
                queue = p.page(page)
            except (EmptyPage, InvalidPage):
                queue = p.page(p.num_pages)

            return queue.object_list
