#coding: utf-8

from videorepo.models import VideoFile, CDNServer, CDNRegion, TransferQueue, SegmentQueue
from django.contrib import admin

admin.site.register(VideoFile)
admin.site.register(CDNServer)
admin.site.register(CDNRegion)
admin.site.register(TransferQueue)
admin.site.register(SegmentQueue)
