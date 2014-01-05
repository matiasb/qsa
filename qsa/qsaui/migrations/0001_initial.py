# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Series'
        db.create_table(u'qsaui_series', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('overview', self.gf('django.db.models.fields.TextField')()),
            ('first_aired', self.gf('django.db.models.fields.DateField')()),
            ('runtime', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('tags', self.gf('django.db.models.fields.TextField')()),
            ('cast', self.gf('django.db.models.fields.TextField')()),
            ('poster', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tvdb_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('imdb_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'qsaui', ['Series'])

        # Adding model 'Season'
        db.create_table(u'qsaui_season', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qsaui.Series'])),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'qsaui', ['Season'])

        # Adding model 'Episode'
        db.create_table(u'qsaui_episode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qsaui.Season'])),
            ('number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('overview', self.gf('django.db.models.fields.TextField')()),
            ('first_aired', self.gf('django.db.models.fields.DateField')()),
            ('image', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('tvdb_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('imdb_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('writer', self.gf('django.db.models.fields.TextField')(null=True)),
            ('director', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'qsaui', ['Episode'])


    def backwards(self, orm):
        # Deleting model 'Series'
        db.delete_table(u'qsaui_series')

        # Deleting model 'Season'
        db.delete_table(u'qsaui_season')

        # Deleting model 'Episode'
        db.delete_table(u'qsaui_episode')


    models = {
        u'qsaui.episode': {
            'Meta': {'object_name': 'Episode'},
            'director': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'first_aired': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'overview': ('django.db.models.fields.TextField', [], {}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qsaui.Season']"}),
            'tvdb_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'writer': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        u'qsaui.season': {
            'Meta': {'object_name': 'Season'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['qsaui.Series']"}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'qsaui.series': {
            'Meta': {'object_name': 'Series'},
            'cast': ('django.db.models.fields.TextField', [], {}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_aired': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'overview': ('django.db.models.fields.TextField', [], {}),
            'poster': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'runtime': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tags': ('django.db.models.fields.TextField', [], {}),
            'tvdb_id': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['qsaui']