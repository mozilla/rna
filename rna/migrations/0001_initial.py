# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Release'
        db.create_table('rna_release', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True)),
            ('product', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('channel', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('release_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('bug_list', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('bug_search_url', self.gf('django.db.models.fields.CharField')(max_length=2000, blank=True)),
            ('system_requirements', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('rna', ['Release'])

        # Adding model 'Note'
        db.create_table('rna_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(db_index=True, blank=True)),
            ('bug', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_known_issue', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fixed_in_release', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fixed_note_set', null=True, to=orm['rna.Release'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('sort_num', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('rna', ['Note'])

        # Adding M2M table for field releases on 'Note'
        m2m_table_name = db.shorten_name('rna_note_releases')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('note', models.ForeignKey(orm['rna.note'], null=False)),
            ('release', models.ForeignKey(orm['rna.release'], null=False))
        ))
        db.create_unique(m2m_table_name, ['note_id', 'release_id'])


    def backwards(self, orm):
        # Deleting model 'Release'
        db.delete_table('rna_release')

        # Deleting model 'Note'
        db.delete_table('rna_note')

        # Removing M2M table for field releases on 'Note'
        db.delete_table(db.shorten_name('rna_note_releases'))


    models = {
        'rna.note': {
            'Meta': {'ordering': "('sort_num',)", 'object_name': 'Note'},
            'bug': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'fixed_in_release': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fixed_note_set'", 'null': 'True', 'to': "orm['rna.Release']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_known_issue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'releases': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['rna.Release']", 'symmetrical': 'False', 'blank': 'True'}),
            'sort_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'rna.release': {
            'Meta': {'ordering': "('product', '-version', 'channel')", 'object_name': 'Release'},
            'bug_list': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bug_search_url': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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