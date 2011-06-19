#coding: utf-8

from videorepo.models import VideoFile, CDNServer, CDNRegion, TransferQueue, Logfile
from videorepo.models import SegmentQueue, VideoProject, ProjectPolicy
from django.contrib import admin


class LogfileAdmin(admin.ModelAdmin):
    list_display = ['server', 'status', 'last_error_msg', 'copy_retry_count', 'logfile']

admin.site.register(VideoFile)
admin.site.register(CDNServer)
admin.site.register(CDNRegion)
admin.site.register(TransferQueue)
admin.site.register(SegmentQueue)
admin.site.register(VideoProject)
admin.site.register(ProjectPolicy)
admin.site.register(Logfile, LogfileAdmin)