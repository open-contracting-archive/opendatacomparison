from django.core.urlresolvers import resolve
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from datamap.views.field import AddFieldView
from .factories import DatamapFactory, FormatFactory


class AddFieldViewTest(TestCase):

    def test_url_passes_datamap_id_to_add_field_view(self):
        view = resolve('/datamap/14/field/edit/')
        self.assertEqual(view.kwargs, {'pk': '14'})

    def test_add_field_view_has_bookmarks_with_datamap(self):
        format = FormatFactory(title='RSS')
        datamap = DatamapFactory(format=format)
        view = AddFieldView.as_view()
        # Snippets we're testing for
        # - basic breadcrump
        # - breadcrumb that links to our map
        desired_html_snippet_1 = '<ol class="breadcrumb">'
        desired_html_snippet_2 = \
            '<li><a href="%s">%s</a></li>' % (
                reverse('datamap', kwargs={'pk': datamap.id}),
                ' '.join((datamap.dataset.title, '-', 'RSS'))
            )

        response = view(RequestFactory().get('/'), pk=str(datamap.id))
        self.assertContains(response, desired_html_snippet_1)
        self.assertContains(response, desired_html_snippet_2)
