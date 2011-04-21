# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'VideoFile'
        db.create_table('videorepo_videofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file_hash', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('upload_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('file_name', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('file_size', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('videorepo', ['VideoFile'])

        # Adding model 'CDNServer'
        db.create_table('videorepo_cdnserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('server_port', self.gf('django.db.models.fields.IntegerField')()),
            ('node_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('cdn_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videorepo.CDNRegion'])),
        ))
        db.send_create_signal('videorepo', ['CDNServer'])

        # Adding model 'CDNRegion'
        db.create_table('videorepo_cdnregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('region_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal('videorepo', ['CDNRegion'])

        # Adding model 'TransferQueue'
        db.create_table('videorepo_transferqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videorepo.VideoFile'])),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videorepo.CDNServer'])),
            ('transfer_type', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('transfer_status', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('max_simultaneous_segments', self.gf('django.db.models.fields.IntegerField')()),
            ('current_segments', self.gf('django.db.models.fields.IntegerField')()),
            ('segment_size', self.gf('django.db.models.fields.IntegerField')()),
            ('max_bandwidth_mbps', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('videorepo', ['TransferQueue'])

        # Adding model 'SegmentQueue'
        db.create_table('videorepo_segmentqueue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('queue_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videorepo.TransferQueue'])),
            ('segment_start', self.gf('django.db.models.fields.IntegerField')()),
            ('segment_end', self.gf('django.db.models.fields.IntegerField')()),
            ('segment_status', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal('videorepo', ['SegmentQueue'])


    def backwards(self, orm):
        
        # Deleting model 'VideoFile'
        db.delete_table('videorepo_videofile')

        # Deleting model 'CDNServer'
        db.delete_table('videorepo_cdnserver')

        # Deleting model 'CDNRegion'
        db.delete_table('videorepo_cdnregion')

        # Deleting model 'TransferQueue'
        db.delete_table('videorepo_transferqueue')

        # Deleting model 'SegmentQueue'
        db.delete_table('videorepo_segmentqueue')


    models = {
        'videorepo.cdnregion': {
            'Meta': {'object_name': 'CDNRegion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'videorepo.cdnserver': {
            'Meta': {'object_name': 'CDNServer'},
            'cdn_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.CDNRegion']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'node_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'server_port': ('django.db.models.fields.IntegerField', [], {})
        },
        'videorepo.segmentqueue': {
            'Meta': {'object_name': 'SegmentQueue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'queue_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.TransferQueue']"}),
            'segment_end': ('django.db.models.fields.IntegerField', [], {}),
            'segment_start': ('django.db.models.fields.IntegerField', [], {}),
            'segment_status': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'videorepo.transferqueue': {
            'Meta': {'object_name': 'TransferQueue'},
            'current_segments': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_bandwidth_mbps': ('django.db.models.fields.IntegerField', [], {}),
            'max_simultaneous_segments': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'segment_size': ('django.db.models.fields.IntegerField', [], {}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.CDNServer']"}),
            'transfer_status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'transfer_type': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'video_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.VideoFile']"})
        },
        'videorepo.videofile': {
            'Meta': {'object_name': 'VideoFile'},
            'file_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'file_name': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'file_size': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['videorepo']
