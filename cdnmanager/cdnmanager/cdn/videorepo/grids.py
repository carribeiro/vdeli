from djangojqgrid.jqgrid import JqGrid
from django.core.urlresolvers import reverse
from videorepo.models import VideoFile

class ProjectGrid(JqGrid):
    model = VideoFile # could also be a queryset
    #fields = ['upload_date', 'file_name', 'file_hash', 'file_size'] # optional 
    url = reverse('grid_handler')
    caption = 'Video Projects Grid' # optional
    colmodel_overrides = {
        'id': { 'editable': True, 'width':10 },
    }
