from mock import Mock

from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse, resolve
from django.test import TestCase, Client
from django.test.client import RequestFactory

from downloads.models import Click
from downloads.views import GetDownloadView
from profiles.tests.factories import UserFactory
from .factories import LinkFactory


class TestGetDownloadView(TestCase):

    def test_get_redirect_url_returns_url_from_pk_in_kwargs(self):
        link_1 = LinkFactory(url='http://correct.com')
        LinkFactory(url='http://incorrect.com')
        view = GetDownloadView.as_view()
        request = RequestFactory().get('/')
        request.user = Mock()
        request.session = Mock()
        request.session.session_key = 'test'
        response = view(request, pk=link_1.id)
        self.assertEqual(response.url,
                         'http://correct.com')

    def test_anonymous_user_correctly_stored(self):
        link = LinkFactory(url='http://correct.com')
        view = GetDownloadView.as_view()
        request = RequestFactory().get('/')
        request.user = Mock()
        request.user.is_authenticated = lambda: False
        request.session = Mock()
        view(request, pk=link.id)
        click = Click.objects.get(link=link)
        self.assertEqual(click.username, '**anonymous**')

    def test_when_no_session_works(self):
        link = LinkFactory(url='http://correct.com')
        view = GetDownloadView.as_view()
        request = RequestFactory().get('/')
        request.user = Mock()
        request.user.is_authenticated = lambda: False
        request.session = SessionStore()
        view(request, pk=link.id)
        click = Click.objects.get(link=link)
        self.assertEqual(click.username, '**anonymous**')

    def test_pk_is_passed_along_in_kwargs_from_url_resolver(self):
        view = resolve('/download/1/')
        self.assertEqual(view.kwargs, {'pk': '1'})

    def test_full_workflow_for_download_click(self):
        """
        When we login a user through the client, and perform a download,
        we expect a click to be generated with that username and we expect
        a proper session_key to be generated. We're checking session_key is
        correct only by ensuring its not 'default' and that it's long enough.
        """
        client = Client()
        link = LinkFactory()
        user = UserFactory()
        user.set_password('test')
        user.save()
        self.assertTrue(client.login(username=user.username,
                                     password='test'))
        url = reverse('download', kwargs={'pk': link.id})
        client.get(url)
        click = Click.objects.get(username=user.username)
        self.assertNotEqual(click.session_key, 'default')
        self.assertTrue(len(click.session_key) > 15)
