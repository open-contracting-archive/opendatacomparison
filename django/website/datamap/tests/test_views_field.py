# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from package.tests.factories import FormatFactory
from datamap.views.field import AddFieldView, EditFieldView
from datamap.forms import FieldForm
from datamap.models import Field, TranslatedField, Concept
from django.contrib.auth.models import AnonymousUser
from .factories import DatamapFactory, DatafieldFactory, TranslatedFieldFactory

from profiles.tests.factories import UserFactory


class AddBasicFieldViewTest(TestCase):

    def setUp(self):
        self.view = AddFieldView.as_view()
        self.user = UserFactory()
        self.get = RequestFactory().get('/')
        self.get.user = self.user
        self.datamap = DatamapFactory()
        self.concept = Concept.objects.create(name='Concept')
        super(AddBasicFieldViewTest, self).setUp()

    def test_datamap_add_and_edit_requires_login(self):
        f = FormatFactory(title="Anything")
        datamap = DatamapFactory(format=f)

        # Drop privileges to test it breaks
        self.get.user = AnonymousUser()
        response = self.view(self.get, dm=str(datamap.id))
        desired_url = "/accounts/login/?next=/"

        # Should redirect to the login page when there is no authenticated user
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.find(desired_url) > -1)

        # Gibe privledges to test that it work
        self.get.user = self.user
        response = self.view(self.get, dm=str(datamap.id))

        # Make sure we get a rendered page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['datamap/field_add.html'])

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
        expected_submit = '<input type="submit" value="save" class="btn btn-default">'  # nopep8
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
                  'concept': self.concept.id,
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean'
                  }
        )

        self.post.user = self.user
        # Do the post
        self.view(self.post, dm=str(self.datamap.id))
        new_field = Field.objects.get(datamap=self.datamap.id)
        self.assertEqual(new_field.fieldname, 'newfieldname')

    def test_successful_post_returns_to_field_page(self):
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'concept': self.concept.id,
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean'
                  }
        )
        self.post.user = self.user

        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        new_field = Field.objects.get()
        self.assertEqual(response.url,
                         reverse('datamap_field',
                                 kwargs={'pk': new_field.id,
                                         'dm': self.datamap.id}))

    def test_post_without_data_returns_form_invalid(self):
        self.post = RequestFactory().post('/', data={})
        self.post.user = self.user
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        assert isinstance(response.context_data.get('form'), FieldForm)
        assert response.context_data.get('form').errors


class AddFieldViewWithTranslationsTest(TestCase):

    def setUp(self):
        self.view = AddFieldView.as_view()
        self.user = UserFactory()
        self.get = RequestFactory().get('/')
        self.get.user = self.user
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
        concept = Concept.objects.create(name='Concept')
        self.post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'concept': concept.id,
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

        self.post.user = self.user
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
        self.post.user = self.user
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
        self.post.user = self.user
        # Do the post
        response = self.view(self.post, dm=str(self.datamap.id))
        expected_form_snippet_1 = 'This field is required.'
        expected_form_snippet_2 = 'value="newfield"'
        self.assertContains(response, expected_form_snippet_1)
        self.assertContains(response, expected_form_snippet_2)


class EditBasicFieldViewTest(TestCase):

    def setUp(self):
        self.view = EditFieldView.as_view()
        self.user = UserFactory()
        self.get = RequestFactory().get('/')
        self.get.user = self.user

        self.datafield = DatafieldFactory(fieldname='testfield')
        self.kwargs = {'dm': '%s' % self.datafield.datamap.id,
                       'pk': '%s' % self.datafield.id}
        super(EditBasicFieldViewTest, self).setUp()

    def test_url_passes_datamap_and_field_id_to_add_field_view(self):
        view = resolve('/datamap/14/field/edit/12/')
        self.assertEqual(view.kwargs, {'dm': '14', 'pk': '12'})

    def test_url_uses_editview_view(self):
        view = resolve('/datamap/14/field/edit/12/')
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
                  'concept': self.datafield.concept.id,
                  'translations-TOTAL_FORMS': u'0',
                  'translations-INITIAL_FORMS': u'0',
                  'translations-MAX_NUM_FORMS': u'',
                  'datatype': 'Boolean',
                  }
        )
        post.user = self.user
        self.view(post, **self.kwargs)
        changed_field = Field.objects.get(pk=self.datafield.id)
        self.assertEqual(changed_field.fieldname, 'changedfieldname')

    def test_helpful_error_message_if_same_fieldname(self):
        pass


class EditFieldWithTranslationsTest(TestCase):

    def setUp(self):
        self.view = EditFieldView.as_view()
        self.user = UserFactory()
        self.get = RequestFactory().get('/')
        self.get.user = self.user
        self.transfield = TranslatedFieldFactory(language='bas')
        self.kwargs = {'dm': '%s' % self.transfield.field.datamap.id,
                       'pk': '%s' % self.transfield.field.id}
        super(EditFieldWithTranslationsTest, self).setUp()

    def test_edit_field_view_has_translatedfield_populated(self):
        desired_html_snippet_1 = ' id="id_translations-0-title" maxlength="100" name="translations-0-title" type="text" value="Ⓣⓨⓟⓔ ⓨⓞⓤⓡ ⓣⓔⓧⓣ ⓗⓔⓡⓔ    " />'  # nopep8
        response = self.view(self.get, **self.kwargs)
        response.render()
        self.assertContains(response, desired_html_snippet_1)

    def test_when_two_translated_fields_shows_all_tab_headers(self):
        TranslatedFieldFactory(field=self.transfield.field, language='da')

        tab_1 = '<a class="lang-tab" href="#tabs-translations-0" id="translations-0">ba</a>'  # nopep8
        tab_2 = '<a class="lang-tab" href="#tabs-translations-1" id="translations-1">da</a>'  # nopep8
        response = self.view(self.get, **self.kwargs)
        self.assertContains(response, tab_1)
        self.assertContains(response, tab_2)

    def test_post_2_translated_field_saves_translated_fields(self):
        transfield_2 = TranslatedFieldFactory(field=self.transfield.field,
                                              language='da')
        self.assertEqual(transfield_2.language, 'da')
        post = RequestFactory().post(
            '/',
            data={'fieldname': 'newfieldname',
                  'concept': self.transfield.field.concept.id,
                  'datatype': 'Boolean',
                  'translations-TOTAL_FORMS': u'2',
                  'translations-INITIAL_FORMS': u'2',
                  'translations-MAX_NUM_FORMS': u'1000',
                  'translations-0-id': self.transfield.id,
                  'translations-0-language': 'en_US',
                  'translations-0-title': 'New Field Name',
                  'translations-1-id': transfield_2.id,
                  'translations-1-language': 'es',
                  'translations-1-title': 'Nuevo Nombre',
                  })

        post.user = self.user
        # Do the post
        response = self.view(post, **self.kwargs)
        self.assertEqual(
            response.status_code,
            302,  # get_success_url is a rediret
            msg="Did not get to success_url, something went wrong"
        )
        transfield_2 = TranslatedField.objects.get(id=transfield_2.id)
        self.assertEqual(transfield_2.language, 'es')

    def test_we_are_not_creating_new_field_object_and_are_adding_trans(self):
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(TranslatedField.objects.count(), 1)
        post = RequestFactory().post(
            '/',
            data={'concept': self.transfield.field.concept.id,
                  'fieldname': self.transfield.field.fieldname,
                  'datatype': self.transfield.field.datatype,

                  'translations-TOTAL_FORMS': u'4',
                  'translations-INITIAL_FORMS': u'1',
                  'translations-MAX_NUM_FORMS': u'1000',

                  'translations-0-id': str(self.transfield.id),
                  'translations-0-field': str(self.transfield.field.id),
                  'translations-0-language': self.transfield.language,
                  'translations-0-title': self.transfield.title,
                  'translations-0-allowable_values': '',
                  'translations-0-description': '',

                  'translations-1-id': '',
                  'translations-1-field': str(self.transfield.field.id),
                  'translations-1-language': 'es',
                  'translations-1-title': 'Nuevo Nombre',
                  'translations-1-allowable_values': '',
                  'translations-1-description': '',

                  'translations-2-id': '',
                  'translations-2-field': str(self.transfield.field.id),
                  'translations-2-language': 'en_US',
                  'translations-2-title': '',
                  'translations-2-allowable_values': '',
                  'translations-2-description': '',

                  'translations-3-id': '',
                  'translations-3-field': str(self.transfield.field.id),
                  'translations-3-language': 'en_US',
                  'translations-3-title': '',
                  'translations-3-allowable_values': '',
                  'translations-3-description': '',
                  })
        post.user = self.user
        # Do the post
        self.view(post, **self.kwargs)
        self.assertEqual(Field.objects.count(), 1)
        self.assertEqual(TranslatedField.objects.count(), 2)
