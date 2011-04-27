# videorepo.forms file

from django import forms
from videorepo.models import VideoProject, ProjectPolicy, CDNRegion
from django.forms.models import inlineformset_factory
from django.forms.widgets import TextInput, Select
from django.contrib.admin import widgets
from django.conf import settings

class MainForm(forms.Form):
    project_name = forms.ModelChoiceField(queryset=VideoProject.objects, empty_label="(select the project)")
    video_file = forms.FileField()

class VideoProjectForm(forms.ModelForm):
    class Meta:
        model = VideoProject
        fields = ['name']

class PolicyProjectForm(forms.ModelForm):
    class Media:
        js = ('/static/admin/js/core.js', '/static/admin/jsi18n/')
    
    class Meta:
        model = ProjectPolicy
        widgets = {
            'max_simultaneous_segments' : TextInput(attrs={'size':'11'}),
            'max_bandwidth_per_segment_kbps' : TextInput(attrs={'size':'11'}),
            'segment_size_kb': TextInput(attrs={'size':'11'}),
            'start_time': TextInput(attrs={'size':'12'}),
            'end_time': TextInput(attrs={'size':'12'}),
        }
    def __init__(self, *args, **kwargs):
        super(PolicyProjectForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].widget = widgets.AdminTimeWidget()
        self.fields['end_time'].widget = widgets.AdminTimeWidget()

ProjectPolicyFormSet = inlineformset_factory(VideoProject, ProjectPolicy, form=PolicyProjectForm, extra=3)