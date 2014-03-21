# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Publisher.name'
        db.alter_column(u'publisher_publisher', 'name', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'Publisher.country'
        db.alter_column(u'publisher_publisher', 'country', self.gf('django.db.models.fields.CharField')(max_length=2))

    def backwards(self, orm):

        # Changing field 'Publisher.name'
        db.alter_column(u'publisher_publisher', 'name', self.gf('django.db.models.fields.CharField')(max_length='50'))

        # Changing field 'Publisher.country'
        db.alter_column(u'publisher_publisher', 'country', self.gf('django_countries.fields.CountryField')(max_length=2))

    models = {
        u'publisher.publisher': {
            'Meta': {'object_name': 'Publisher'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['publisher']