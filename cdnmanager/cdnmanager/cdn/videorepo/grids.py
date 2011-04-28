from djangojqgrid.jqgrid import JqGrid
from django.core.urlresolvers import reverse
from videorepo.models import VideoFile, TransferQueue
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

def VideoFilesByUserGrid(user=None):
    """ Class/instance factory. See ticket #23. 
        This factory function creates a new class and instantiates it.
        The reason is because the model field has to be defined at runtime,
        but it is a class attribute, so the need to redeclare the class.
    """

    class VideoFilesByUserGrid(JqGrid):
        if user is None:
            model = VideoFile
        else:
            queryset = VideoFile.objects.select_related().filter(
                        project__user__id=user.id, 
                        project__isnull=False
                        )

        url = reverse('video_files_by_user_grid_handler')
        caption = _('Video files by user') # optional
        # TODO: tried to improve the grid, printing a calculated field that had only 
        # the "short" or base file name for the file. It didn't work with the Jqgrid.
        fields = ('project__name', 'file_name_short', 'file_size', 'file_hash',  'upload_date')
        colmodel_overrides = {
            'project__name': { 'width': 80 },
            #'file_name': { 'name': 'File name' },
            'file_size': { 'align':'right', 'editable': False, 'width':30 },
            'upload_date': { 'align':'center', 'width': 60 }
        }

    # returns an instance of the class
    return VideoFilesByUserGrid()

def TransferQueueGrid(user=None):
    """ Shows the video transfer queue
    """

    class TransferQueueGrid(JqGrid):
        if user is None:
            model = TransferQueue
        else:
            queryset = TransferQueue.objects.select_related().all()

        url = reverse('transfer_queue_grid_handler')
        caption = _('Transfer Queue') # optional
        # TODO: tried to improve the grid, printing a calculated field that had only 
        # the "short" or base file name for the file. It didn't work with the Jqgrid.
        fields = ('video_file__file_name_short', 'server__node_name', 'server__ip_address', 
                  'video_file__file_size', 'transfer_method', 'transfer_status')
        colmodel_overrides = {
            #'file_name': { 'name': 'File name' },
            'file_size': { 'align':'right', 'width':30 },
        }

    # returns an instance of the class
    return TransferQueueGrid()