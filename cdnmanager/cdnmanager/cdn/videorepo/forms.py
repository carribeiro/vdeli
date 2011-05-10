# videorepo.forms file

from django import forms
from videorepo.models import VideoProject, ProjectPolicy, CDNRegion, VideoFile
from django.forms.models import inlineformset_factory
from django.forms.widgets import TextInput, Select
from django.contrib.admin import widgets
from django.conf import settings

class MainForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MainForm, self).__init__(*args, **kwargs)
        self.fields['project_name'].queryset = VideoProject.objects.filter(user=self.user)

    project_name = forms.ModelChoiceField(queryset=VideoProject.objects, empty_label="(select the project)")
    video_file = forms.FileField(label='Video File')

class VideoProjectForm(forms.ModelForm):
    class Meta:
        model = VideoProject
        fields = ['name']

class PolicyProjectForm(forms.ModelForm):

    class Media:
        js = ('/static/admin/js/core.js', '/static/admin/jsi18n/')

    class Meta:
        model = ProjectPolicy
        fields = ('cdnregion', 'transfer_method' , 'protocol',
                  'max_simultaneous_segments', 'max_bandwidth_per_segment_kbps',
                  'segment_size_kb', 'start_time', 'end_time')
        widgets = {
            'max_simultaneous_segments' : TextInput(attrs={'size':'8'}),
            'max_bandwidth_per_segment_kbps' : TextInput(attrs={'size':'8'}),
            'segment_size_kb': TextInput(attrs={'size':'8'}),
            'start_time': TextInput(attrs={'size':'12'}),
            'end_time': TextInput(attrs={'size':'12'}),
        }
    def __init__(self, *args, **kwargs):
        super(PolicyProjectForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].widget = widgets.AdminTimeWidget()
        self.fields['end_time'].widget = widgets.AdminTimeWidget()

ProjectPolicyFormSet = inlineformset_factory(VideoProject, ProjectPolicy, form=PolicyProjectForm, extra=3)
