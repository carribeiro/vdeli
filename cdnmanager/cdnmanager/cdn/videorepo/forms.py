# videorepo.forms file

from django import forms
from videorepo.models import VideoProject, ProjectPolicy, CDNRegion
from django.forms.models import inlineformset_factory

class MainForm(forms.Form):
    project_name = forms.ModelChoiceField(queryset=VideoProject.objects, empty_label="(select the project)")
    video_file = forms.FileField()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = VideoProject

ProjectPolicyFormSet = inlineformset_factory(VideoProject, ProjectPolicy)