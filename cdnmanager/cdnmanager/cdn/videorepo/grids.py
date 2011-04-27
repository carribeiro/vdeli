from djangojqgrid.jqgrid import JqGrid
from django.core.urlresolvers import reverse
from videorepo.models import VideoFile
from django.contrib.auth.models import User

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

        #fields = ['upload_date', 'file_name', 'file_hash', 'file_size'] # optional 
        url = reverse('video_files_by_user_grid_handler')
        caption = 'Video files by user' # optional
        colmodel_overrides = {
            'id': { 'editable': True, 'width':10 },
        }

    # returns an instance of the class
    return VideoFilesByUserGrid()