# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Note.sort_num'
        if not db.dry_run:
            orm['rna.Note'].objects.filter(sort_num=None).update(sort_num=0)
        db.alter_column(u'rna_note', 'sort_num', self.gf('django.db.models.fields.IntegerField')())

    def backwards(self, orm):

        # Changing field 'Note.sort_num'
        db.alter_column(u'rna_note', 'sort_num', self.gf('django.db.models.fields.IntegerField')(null=True))

    models = {
        u'rna.note': {
            'Meta': {'object_name': 'Note'},
            'bug': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'fixed_in_release': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fixed_note_set'", 'null': 'True', 'to': u"orm['rna.Release']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_known_issue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'releases': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rna.Release']", 'symmetrical': 'False', 'blank': 'True'}),
            'sort_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'rna.release': {
            'Meta': {'ordering': "('product', '-version', 'channel')", 'unique_together': "(('product', 'version'),)", 'object_name': 'Release'},
            'bug_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bug_search_url': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {}),
            'system_requirements': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['rna']
