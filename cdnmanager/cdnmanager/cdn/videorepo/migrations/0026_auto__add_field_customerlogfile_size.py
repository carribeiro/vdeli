# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CustomerLogfile.size'
        db.add_column('videorepo_customerlogfile', 'size', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CustomerLogfile.size'
        db.delete_column('videorepo_customerlogfile', 'size')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'password': ('django.db.models.fields.CharField', [], {'default': "'vDe11Admin'", 'max_length': '20'}),
            'server_port': ('django.db.models.fields.IntegerField', [], {}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'Europe/Moscow'", 'max_length': '100'}),
            'username': ('django.db.models.fields.CharField', [], {'default': "'vdeliadmin'", 'max_length': '20'})
        },
        'videorepo.customerlogfile': {
            'Meta': {'object_name': 'CustomerLogfile'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'fpath': ('django.db.models.fields.CharField', [], {'max_length': '360'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'videorepo.logfile': {
            'Meta': {'object_name': 'Logfile'},
            'copy_retry_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'copy_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error_msg': ('django.db.models.fields.CharField', [], {'default': "'No Errors'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'log_length': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'log_lines': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'logfile': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.CDNServer']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'timestamp': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        'videorepo.projectpolicy': {
            'Meta': {'object_name': 'ProjectPolicy'},
            'cdnregion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.CDNRegion']"}),
            'end_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_bandwidth_per_segment_kbps': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'max_simultaneous_segments': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'HTTP'", 'max_length': '5'}),
            'segment_size_kb': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.TimeField', [], {'default': 'datetime.time(0, 0)'}),
            'transfer_method': ('django.db.models.fields.CharField', [], {'default': "'Single FTP'", 'max_length': '15'}),
            'video_project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.VideoProject']"})
        },
        'videorepo.segmentqueue': {
            'Meta': {'object_name': 'SegmentQueue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'queue_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.TransferQueue']"}),
            'segment_end': ('django.db.models.fields.IntegerField', [], {}),
            'segment_start': ('django.db.models.fields.IntegerField', [], {}),
            'segment_status': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'videorepo.summarylog': {
            'Meta': {'object_name': 'SummaryLog'},
            'concurrent_requests': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_requests': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.IntegerField', [], {}),
            'total_transfer_mb': ('django.db.models.fields.IntegerField', [], {}),
            'video_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.VideoFile']"})
        },
        'videorepo.transferqueue': {
            'Meta': {'object_name': 'TransferQueue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_error_msg': ('django.db.models.fields.CharField', [], {'default': "'No Errors'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_bandwidth_kbps': ('django.db.models.fields.IntegerField', [], {}),
            'max_simultaneous_segments': ('django.db.models.fields.IntegerField', [], {}),
            'percentage_transferred': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'segment_size_kb': ('django.db.models.fields.IntegerField', [], {}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.CDNServer']"}),
            'transfer_method': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'transfer_status': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'video_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.VideoFile']"})
        },
        'videorepo.videofile': {
            'Meta': {'object_name': 'VideoFile'},
            'file_hash': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'file_name': ('django.db.models.fields.files.FileField', [], {'max_length': '250'}),
            'file_name_short': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '120'}),
            'file_size': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videorepo.VideoProject']", 'null': 'True'}),
            'upload_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'videorepo.videoproject': {
            'Meta': {'object_name': 'VideoProject'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['videorepo']
