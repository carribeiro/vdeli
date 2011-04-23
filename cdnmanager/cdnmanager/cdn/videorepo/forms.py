# videorepo.forms file

from django import forms
from models import VideoProject

class MainForm(forms.Form):
    project_name = forms.ModelChoiceField(queryset=VideoProject.objects, empty_label="(select the project)")
    video_file = forms.FileField()
