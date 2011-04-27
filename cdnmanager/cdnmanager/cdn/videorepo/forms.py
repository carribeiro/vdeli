# videorepo.forms file

from django import forms
from videorepo.models import VideoProject, ProjectPolicy, CDNRegion
from django.forms.models import inlineformset_factory
from django.forms.widgets import TextInput, Select

class MainForm(forms.Form):
    project_name = forms.ModelChoiceField(queryset=VideoProject.objects, empty_label="(select the project)")
    video_file = forms.FileField()

class VideoProjectForm(forms.ModelForm):
    class Meta:
        model = VideoProject
        fields = ['name']

class PolicyProjectForm(forms.ModelForm):
    class Meta:
        model = ProjectPolicy
        widgets = {
            'max_simultaneous_segments' : TextInput(attrs={'size':'11'}),
            'max_bandwidth_per_segment_kbps' : TextInput(attrs={'size':'11'}),
            'segment_size_kb': TextInput(attrs={'size':'11'}),
        }

ProjectPolicyFormSet = inlineformset_factory(VideoProject, ProjectPolicy, form=PolicyProjectForm, extra=3)