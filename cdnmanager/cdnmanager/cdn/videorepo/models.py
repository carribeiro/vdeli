#coding: utf-8

import os.path
import time
import datetime
import settings

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


# Create your models here.

class VideoFile(models.Model):
    """
    Represents a video file in th CDN. The video is uploaded once, in the
    manager, but is replicated to all the other CDN servers.
    """
    file_hash = models.CharField(_('file hash'), max_length=200)
    upload_date = models.DateTimeField(_('upload date'))
    # todo: check if the upload_to directory is the one being used. seems to be inconsistent with other configs.
    file_name = models.FileField(_('file name full'),upload_to='video_files',max_length=250)
    file_name_short = models.CharField(_('file name short'),default='',max_length=120)
    file_size = models.IntegerField(_('file size'))
    project = models.ForeignKey('VideoProject',null=True)

    @classmethod
    def from_file_name(cls, video_file_name, project):
        # calculate the SHA1 hash
        import hashlib
        with open(video_file_name, "rb") as f:
            CHUNK_SIZE = 1024*1024
            buf = f.read(CHUNK_SIZE)
            h = hashlib.sha1()
            while buf:
                h.update(buf)
                buf = f.read(CHUNK_SIZE)

        # how to create a filefield programatically
        # http://groups.google.com/group/django-users/browse_thread/thread/184e5e09db1efce4
        path, fnshort = os.path.split(str(video_file_name))
        return VideoFile(file_name=video_file_name, 
                         file_size=os.path.getsize(video_file_name),
                         file_name_short=fnshort,
                         file_hash=h.hexdigest(),
                         upload_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 
                         project=project)

    def make_file_name_short(self):
        path, fnshort = os.path.split(str(self.file_name))
        self.file_name_short = fnshort
        return fnshort

    def __unicode__(self):
        return "VideoFile %s (%d bytes)" % (
            os.path.relpath(str(self.file_name), settings.MEDIA_ROOT), 
            self.file_size)

class SummaryLog(models.Model):
    """
    This model stores 5 minute interval samples with the number of videos
    being requested and other data. The table is generated from a long 
    running process that takes log files from the servers and summarize
    the data per interval.

    To make things easier, the start_time is recorded as a integer, as
    'seconds since epoch' format. This format makes it easier to write
    queries that summarize the data per hour or day, as it is just a 
    matter of selecting a integer interval (ex: one hour = 12 samples).
    """
    video_file = models.ForeignKey('VideoFile')
    start_time = models.IntegerField()
    new_requests = models.IntegerField()
    concurrent_requests = models.IntegerField()
    total_transfer_mb = models.IntegerField()
    # interrupted_transfers = models.IntegerField()  # check if we have this info

class CDNServer(models.Model):
    """
    Represents a single CDN server.
    """
    ip_address = models.IPAddressField('Endereço IP')
    server_port = models.IntegerField('Porta do Servidor CDN')
    node_name = models.CharField('Nome do Nodo', max_length=60)
    cdn_group = models.ForeignKey('CDNRegion')

    def __unicode__(self):
        return "%s (ip:%s, group:%s)" % (self.node_name, self.ip_address, self.cdn_group.region_name)

# We will include a CDNCluster entity later. For now, every cluster has only one server.

class CDNRegion(models.Model):
    """
    Represents a region, or group of clusters/servers. This information
    allows the user to configure distribution policies for all the servers
    inside a given region.
    """
    region_name = models.CharField('Region name', max_length=60)

    def __unicode__(self):
        return self.region_name

class TransferQueue(models.Model):
    video_file = models.ForeignKey('VideoFile')
    server = models.ForeignKey('CDNServer')
    transfer_method = models.CharField(max_length=15)
    transfer_status = models.CharField(max_length=15)
    # all the following fields are in fact derived from transfer_type. i'm
    # still not sure about the best way to deal with it, so I'll leave some
    # duplication to check which model is best - normalization or 
    # non-normalization
    protocol = models.CharField(max_length=5)
    max_simultaneous_segments = models.IntegerField()
    segment_size_kb = models.IntegerField()
    max_bandwidth_kbps = models.IntegerField()
    percentage_transferred = models.IntegerField(default=0)

    # todo: transferqueue also has to refer to the policy and region because the same 
    # server can be found in several regions/policies.
    def __unicode__(self):
        return "Project:%s, video:%s, server:%s, method:%s, status:%s, speed:%d" % ( 
            self.video_file.project.name,
            self.video_file.file_name, 
            self.server.node_name,
            self.transfer_method,
            self.transfer_status,
            self.max_bandwidth_kbps)
    
class SegmentQueue(models.Model):
    """
    Represents a file segment scheduled for transfer, transferred, suspended, or cancelled.
    """
    queue_entry = models.ForeignKey('TransferQueue')
    segment_start = models.IntegerField()
    segment_end = models.IntegerField()
    # waiting, transferring, complete, suspendend, cancelled,
    segment_status = models.CharField(max_length=15)
    
class VideoProject(models.Model):
    """
    Each video is part of a project. The project has a name and and is 
    associated with the user. A project has also one or more policies
    that control file replication on the CDN servers.
    """
    name = models.CharField(_('Project Name'), max_length=30)
    creation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "Project:%s, user:%s" % (self.name, self.user.username)

TRANSFER_METHOD_CHOICES = (
    ('Single HTTP', 'Single HTTP transfer'),
    ('Single FTP', 'Single FTP transfer'),
    ('Torrent-like', 'Fast HTTP (torrent-like)'),
    ('Trickle', 'Rate Controlled FTP'),
)

PROTOCOL_CHOICES = (
    ('FTP', 'FTP'),
    ('HTTP', 'HTTP'),
)

class ProjectPolicy(models.Model):
    """
    Each policy defines how a video should be transferred, and to which
    servers.
    """
    video_project = models.ForeignKey(VideoProject)
    cdnregion = models.ForeignKey(CDNRegion)
    transfer_method = models.CharField(_('Transfer type'), max_length=15,
        choices=TRANSFER_METHOD_CHOICES,
        default='Single FTP')
    protocol = models.CharField(_('Protocol'), max_length=5, default='HTTP',
                                choices=PROTOCOL_CHOICES,)
    max_simultaneous_segments = models.IntegerField(_('Max Conn'),
                                default=1)
    segment_size_kb = models.IntegerField(_('Seg. size (kB)'),
                                default=0)
    max_bandwidth_per_segment_kbps = models.IntegerField(_('Max BW (kbps)'),
                                default=0)
    start_time = models.TimeField(_('Sync Window Start'),
                                default=datetime.time(00,00))
    end_time = models.TimeField(_('Sync Window End'),
                                default=datetime.time(00,00))

    class Meta:
        verbose_name_plural = "project policies"

    def __unicode__(self):
        return "Policy:%s, project:%s, region:%s, user: %s" % (
            self.id, self.video_project.name, self.cdnregion.region_name, self.video_project.user.username)

class Logfile(models.Model):
   """ (I’ll have to fix these quotes later :-/)
   Logfile is used to track the status of the logfiles retrieved from the
   CDNservers. A new Logfile entry is created by a periodic task, before
   copying the logfile to the cdnmanager.

   - We should really be careful about timezones. Each server is configured
     to it’s own timezone. At 00:00 localtime the logfile is rotated. The
     cdnmanager needs to copy the logfile after it is rotated. As we may
     have several severs in different timezones, the cdnmanager must check
     it every hour.

   - Possible status:
     notcopied   The logfile entry was created but the file copy has
                 not started yet. If the filecopy fails, the logfile entry
                 reverts to this status.
     copying     This status is set during the logfile copy.
     copied      Right after finishing the copy, and before starting the
                 filtering process.
     filtering   After copying the logfile, it has to be filtered. We
                 need to to separate the lines by customer in order to
                 generate the “per customer log file”.
     completed   The logfile was copied and filtered.
     ignore      Used to mark a file that should not be copied. For instance,
                 if we know that a server had a problem or something like
                 that, we can just set the status to ‘ignore’.
   """
   server = models.ForeignKey('CDNServer')
   status = models.CharField(max_length=10)
   log_length = models.IntegerField()  # total length in chars
   log_lines = models.IntegerField()   # total lines

   # log the date&time when the logfile entry was created
   creation_time = models.DateTimeField(_('Creation Time'), auto_now=True)

   # log the date&time when the filecopy was finished
   copy_time = models.DateTimeField(_('Copy Time'), null=True)

   # last_error_msg is a string that can be used to write any message
   # about the last error that happened, for instance: logfile does not
   # exist at the server, sftp timeout, empty file, etc.
   last_error_msg = models.CharField(max_length=100)