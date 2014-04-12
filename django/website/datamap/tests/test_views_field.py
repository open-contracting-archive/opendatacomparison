from __future__ import unicode_literals
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from package.tests.factories import FormatFactory
from datamap.views.field import AddFieldView, EditFieldView
from datamap.forms import FieldForm
from datamap.models import Field, TranslatedField
from .factories import DatamapFactory, DatafieldFactory


class AddBasicFieldViewTest(TestCase):

    def setUp(self):
        self.view = AddFieldView.as_view()
        self.get = RequestFactory().get('/')
        self.datamap = DatamapFactory()
        super(AddBasicFieldViewTest, self).setUp()

    def test_url_passes_datamap_id_to_add_field_view(self):
        view = resolve('/datamap/14/field/edit/')
        self.assertEqual(view.kwargs, {'dm': '14'})

    def test_url_uses_addview_view(self):
        view = resolve('/datamap/14/field/edit/')
        self.assertEqual(view.func.func_name, 'AddFieldView')

    def test_add_field_view_has_bookmarks_with_datamap(self):
        f = FormatFactory(title='RSS')
        datamap = DatamapFactory(format=f)
        # Snippets we're testing for
        # - basic breadcrump
        # - breadcrumb that links to our map
        desired_html_snippet_1 = '<ol class="breadcrumb">'
        desired_html_snippet_2 = \
            '<li><a href="%s">%s</a></li>' % (
                reverse('datamap', kwargs={'pk': datamap.id}),
                ' '.join((datamap.dataset.title, '-', 'RSS'))
            )
        response = self.view(self.get, dm=str(datamap.id))
        response.render()
        self.assertContains(response, desired_html_snippet_1)
        self.assertContains(response, desired_html_snippet_2)

    def test_context_contains_an_instance_of_field_model_form(self):
        response = self.view(self.get, dm=str(self.datamap.id))
        assert isinstance(response.context_data.get('form'), FieldForm)

    def test_get_renders_field_form(self):
        response = self.view(self.get, dm=str(self.datamap.id))
        expected_form_snippet = '<label for="id_concept">Concept:</label>'
        expected_form_head = '<form role="form" class="form" action="." method="POST">'  # nopep8
        expected_submit = '<input type="submit" value="save" name="add" class="btn btn-default">'  # nopep8
        self.assertContains(response, expected_form_snippet)
        self.assertContains(response, expected_form_head)
        self.assertContains(response, expected_submit)

    def test_get_does_not_have_datamap_input_in_it(self):
        # The datamap will be calculated from the URL
        response = self.view(self.get, dm=str(self.datamap.id))
        unexpected_form_snippet = '<label for="id_datamap">Datamap:</label>'
        self.assertNotContains(response, unexpected_form_snippet)

    def test_get_does_not_have_mapto_input_in_it(self):
        # We will handle mapto somewhere else
        response = self.view(self.get, dm=str(self.datamap.id))
        unexpected_form_snippet = '<label for="id_mapsto">Mapsto:</label>'
        self.assertNotContains(response, unexpected_form_snippet)

    def test_post_with_fieldname_and_type_adds_new_field(self):
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean'
                  }
        )
        # Do the post
        self.view(self.post, dm=str(self.datamap.id))
        new_field = Field.objects.get(datamap=self.datamap.id)
        self.assertEqual(new_field.fieldname, 'newfieldname')

    def test_successful_post_returns_to_datamap_page(self):
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean'
                  }
        )
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        self.assertEqual(response.url,
                         reverse('datamap', kwargs={'pk': self.datamap.id}))

    def test_post_without_data_returns_form_invalid(self):
        self.post = RequestFactory().post('/', data={})
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        assert isinstance(response.context_data.get('form'), FieldForm)
        assert response.context_data.get('form').errors


class AddFieldViewWithTranslationsTest(TestCase):

    def setUp(self):
        self.view = AddFieldView.as_view()
        self.get = RequestFactory().get('/')
        self.datamap = DatamapFactory()
        super(AddFieldViewWithTranslationsTest, self).setUp()

    def test_get_renders_field_form(self):
        response = self.view(self.get, dm=str(self.datamap.id))
        expected_form_snippet = '<label for="id_translations-0-language">Language:</label>'  # nopep8
        expected_form_snippet_2 = '<label for="id_translations-0-title">Title:</label>'  # nopep8
        self.assertContains(response, expected_form_snippet)
        self.assertContains(response, expected_form_snippet_2)

    def test_get_has_hidden_field_with_field_in_it(self):
        # We will handle mapto somewhere else
        response = self.view(self.get, dm=str(self.datamap.id))
        unexpected_form_snippet = '<label for="id_translations-0-field">Field:</label>'  # nopep8
        expected_form_snippet = '<input id="id_translations-0-field" name="translations-0-field" type="hidden" />'  # nopep8
        self.assertNotContains(response, unexpected_form_snippet)
        self.assertContains(response, expected_form_snippet)

    def test_post_with_translated_field_adds_new_translated_fields(self):
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'datatype': 'Boolean',
                  'translations-TOTAL_FORMS': u'2',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'1000',
                  'translations-0-language': 'en_US',
                  'translations-0-title': 'New Field Name',
                  'translations-1-language': 'es',
                  'translations-1-title': 'Nuevo Nombre',
                  })
        # Do the post
        self.view(self.post, dm=str(self.datamap.id))
        transfield = TranslatedField.objects.get(
            field__datamap=self.datamap.id,
            language='en_US'
        )
        self.assertEqual(TranslatedField.objects.count(), 2)
        self.assertEqual(transfield.field.fieldname, 'newfieldname')
        self.assertEqual(transfield.title, 'New Field Name')

    def test_post_with_missing_field_data_returns_field_form_and_formset(self):
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': '',  # Missing DATA
                  'datatype': 'Boolean',
                  'translations-TOTAL_FORMS': u'1',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'1000',
                  'translations-0-language': 'en_US',
                  'translations-0-title': 'New Field Name',
                  })
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        expected_form_snippet_1 = 'This field is required.'
        expected_form_snippet_2 = 'value="New Field Name"'
        self.assertContains(response, expected_form_snippet_1)
        self.assertContains(response, expected_form_snippet_2)

    def test_post_with_missing_translation_data_returns_field_form_and_formset(self):  # nopep8
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfield',
                  'datatype': 'Boolean',
                  'translations-TOTAL_FORMS': u'1',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'1000',
                  'translations-0-language': '',  # Missing DATA
                  'translations-0-title': 'New Field Name',
                  })
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        expected_form_snippet_1 = 'This field is required.'
        expected_form_snippet_2 = 'value="newfield"'
        self.assertContains(response, expected_form_snippet_1)
        self.assertContains(response, expected_form_snippet_2)


class EditBasicFieldViewTest(TestCase):

    def setUp(self):
        self.view = EditFieldView.as_view()
        self.get = RequestFactory().get('/')
        self.datafield = DatafieldFactory(fieldname = 'testfield')
        self.kwargs = {'dm' : '%s' % self.datafield.datamap.id,
                       'pk' : '%s' % self.datafield.id}
        super(EditBasicFieldViewTest, self).setUp()

    def test_url_passes_datamap_and_field_id_to_add_field_view(self):
        view = resolve('/datamap/14/field/edit/12')
        self.assertEqual(view.kwargs, {'dm': '14', 'pk': '12'})

    def test_url_uses_editview_view(self):
        view = resolve('/datamap/14/field/edit/12')
        self.assertEqual(view.func.func_name, 'EditFieldView')

    def test_edit_field_view_has_bookmarks_with_datamap(self):
        desired_html_snippet_1 = 'edit field testfield'
        response = self.view(self.get, **self.kwargs)
        self.assertContains(response, desired_html_snippet_1)

    def test_edit_field_view_has_field_populated(self):
        desired_html_snippet_1 = 'id="id_fieldname" maxlength="100" name="fieldname" type="text" value="testfield" />'  # nopep8
        response = self.view(self.get, **self.kwargs)
        self.assertContains(response, desired_html_snippet_1)

    def test_edit_field_post_changes_fieldname_to_changed(self):
        post = RequestFactory().post(
            '/',
            data={'fieldname': 'changedfieldname',
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean',
                  }
        )
        self.view(post, **self.kwargs)
        changed_field = Field.objects.get(pk=self.datafield.id)
        self.assertEqual(changed_field.fieldname, 'changedfieldname')
