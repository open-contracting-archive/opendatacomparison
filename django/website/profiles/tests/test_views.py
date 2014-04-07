from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from core.tests.data import OpenComparisonTestCase, STOCK_PASSWORD
from profiles.models import Profile


class TestProfile(OpenComparisonTestCase):

    def setUp(self):
        super(TestProfile, self).setUp()
        self.user = User.objects.get(username="user")
        self.profile, created = Profile.objects.get_or_create(user=self.user)

    def test_view(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=STOCK_PASSWORD))
        url = reverse('profile_detail', args=(self.user.username,))
        response = self.client.get(url)
        self.assertContains(response, "Profile for user")

    def test_view_not_loggedin(self):
        url = reverse('profile_detail', args=(self.user.username,))
        response = self.client.get(url)
        self.assertContains(response, "Profile for user")

    def test_edit(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=STOCK_PASSWORD))
        # give me a view
        url = reverse('profile_edit', args=(self.user.username,))
        response = self.client.get(url)
        stuff = """<input class="urlinput form-control" id="id_url" maxlength="200" name="url" type="url" />"""  # nopep8
        self.assertContains(response, stuff)

        # submit some content
        data = {'url': 'http://www.zerg.com'}
        response = self.client.post(url, data, follow=True)
        self.assertContains(response, "Profile for user")
        p = Profile.objects.get(user=self.user)
        self.assertEquals(p.url, "http://www.zerg.com/")
