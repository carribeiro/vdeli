from djangojqgrid import jqgrid
from videorepo import VideoProject
class ProjectGrid(JqGrid):
    model = SomeFancyModel # could also be a queryset
    fields = ['id', 'name', 'desc'] # optional 
    url = reverse('grid_handler')
    caption = 'My First Grid' # optional
    colmodel_overrides = {
        'id': { 'editable': False, 'width':10 },
    }
