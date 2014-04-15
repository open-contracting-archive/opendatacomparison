# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datamap.views.datamap_basic import DatamapAddView
from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory

from package.tests.factories import FormatFactory, DatasetFactory
from datamap.models import Datamap
from .factories import DatamapFactory


class DatamapAddViewTest(TestCase):
    def setUp(self):
        self.view = DatamapAddView.as_view()
        self.get = RequestFactory().get('/')
        self.post = RequestFactory().post('/')
        self.dataset = DatasetFactory()
        self.datamap = DatamapFactory()
        self.format = FormatFactory()
        self.notes = u'Unit test'
        super(DatamapAddViewTest, self).setUp()

    def test_no_datamap_id_is_404(self):
        self.assertRaises(Http404, self.view, self.get)
        self.assertRaises(Http404, self.view, self.post)

    def test_add_datamap_access_denied_when_anonymous(self):
        pass

    def test_add_datamap_view_has_form_fields(self):
        get_request = RequestFactory().get('/datamap/edit/?dataset=%s' % self.dataset.id)

        # Snippets we're testing for
        # - basic breadcrumb
        # - dataset form selector
        # - format form selector
        # - notes form text area
        breadcrumb_snippet = '<ol class="breadcrumb">'
        dataset_select_snippet = '<select class="form-control" id="id_dataset" name="dataset">'
        format_select_snippet = '<select class="form-control" id="id_format" name="format">'
        notes_textarea_snippet = 'id="id_notes"'

        response = self.view(get_request)
        response.render()

        print response

        self.assertContains(response, breadcrumb_snippet)
        self.assertContains(response, dataset_select_snippet)
        self.assertContains(response, format_select_snippet)
        self.assertContains(response, notes_textarea_snippet)

    def test_new_datamap_detects_empty_format(self):
        post_request = RequestFactory().post(
            '/datamap/edit/',
            data={'dataset': str(self.dataset.id),
                  'format': '',
                  'notes': ''}
        )
        # Do the post
        response = self.view(post_request)
        response.render()

        self.assertContains(response, 'errorlist')

    def test_new_datamap_saves_without_error(self):
        post_request = RequestFactory().post(
            '/datamap/edit/',
            data={'add': u'save datamap',
                  'dataset': unicode(self.dataset.id),
                  'format': unicode(self.format.id),
                  'notes': self.notes}
        )
        # Do the post
        response = self.view(post_request)

        self.assertEqual(response.status_code, 302)

        # Make sure that data is correctly stored
        datamap = Datamap.objects.last()
        self.assertIsNotNone(datamap)
        self.assertEqual(datamap.format.title, self.format.title)
        self.assertEqual(datamap.notes, self.notes)
