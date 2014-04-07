from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from package.models import Category, Package

from core.tests.data import STOCK_PASSWORD
from .data import PackageTestCase


@override_settings(RESTRICT_PACKAGE_EDITORS=False)
class FunctionalPackageTest(PackageTestCase):

    def test_package_list_view(self):
        url = reverse('packages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'package/package_list.html')
        packages = Package.objects.all()
        for p in packages:
            self.assertContains(response, p.title)

    def test_package_detail_view(self):
        url = reverse('package', kwargs={'slug': 'testability'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'package/package.html')
        p = Package.objects.get(slug='testability')
        self.assertContains(response, p.title)
        self.assertContains(response, p.description)
        for g in p.grids.all():
            self.assertContains(response, g.title)

    def test_latest_packages_view(self):
        url = reverse('latest_packages')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'package/package_archive.html')
        packages = Package.objects.all()
        for p in packages:
            self.assertContains(response, p.title)
            self.assertContains(response, p.description)

    def test_add_package_view(self):
        url = reverse('add_package')
        response = self.client.get(url)

        # The response should be a redirect, since the user is not logged in.
        self.assertEqual(response.status_code, 302)

        # Once we log in the user, we should get back the appropriate response.
        self.assertTrue(self.client.login(username='user',
                                          password=STOCK_PASSWORD))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'package/package_form.html')
        for c in Category.objects.all():
            self.assertContains(response, c.title)
        count = Package.objects.count()
        category = Category.objects.all()[0].pk
        response = self.client.post(url, {
            'category': category,
            'url': 'https://github.com/django/django',
            'slug': 'django22',
            'title': 'django',
            'translations-TOTAL_FORMS': 0,
            'translations-INITIAL_FORMS': 0,
            'translations-MAX_NUM_FORMS': 1000,
        })
        print response.content
        self.assertEqual(Package.objects.count(), count + 1)
        self.assertEqual(response.status_code, 302)

    def test_edit_package_view(self):
        p = Package.objects.get(slug='testability')
        url = reverse('edit_package', kwargs={'slug': 'testability'})
        response = self.client.get(url)

        # The response should be a redirect, since the user is not logged in.
        self.assertEqual(response.status_code, 302)

        # Once we log in the user, we should get back the appropriate response.
        self.assertTrue(self.client.login(username='user',
                                          password=STOCK_PASSWORD))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'package/package_form.html')
        self.assertContains(response, p.title)
        self.assertContains(response, p.slug)

        # Make a test post
        response = self.client.post(url, {
            'category': Category.objects.all()[0].pk,
            'url': 'https://github.com/django/django',
            'slug': p.slug,
            'title': 'TEST TITLE',
            'translations-TOTAL_FORMS': 0,
            'translations-INITIAL_FORMS': 0,
            'translations-MAX_NUM_FORMS': 1000,
        })
        self.assertEqual(response.status_code, 302)

        # Check that it actually changed the package
        p = Package.objects.get(slug='testability')
        self.assertEqual(p.title, 'TEST TITLE')

    def test_usage_view(self):
        url = reverse('usage', kwargs={'slug': 'testability', 'action': 'add'})
        response = self.client.get(url)

        # The response should be a redirect, since the user is not logged in.
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(username='user')
        count = user.package_set.count()
        self.assertTrue(self.client.login(username='user',
                                          password=STOCK_PASSWORD))

        # Now that the user is logged in, make sure that the number of packages
        # they use has increased by one.
        response = self.client.get(url)
        self.assertEqual(count + 1, user.package_set.count())

        # Now we remove that same package from the user's list
        # of used packages,
        # making sure that the total number has decreased by one.
        url = reverse('usage', kwargs={'slug': 'testability',
                                       'action': 'remove'})
        response = self.client.get(url)
        self.assertEqual(count, user.package_set.count())


class PackagePermissionTest(PackageTestCase):
    def setUp(self):
        super(PackagePermissionTest, self).setUp()
        settings.RESTRICT_PACKAGE_EDITORS = True
        self.test_add_url = reverse('add_package')
        self.test_edit_url = reverse('edit_package',
                                     kwargs={'slug': 'testability'})
        self.login = self.client.login(username='user',
                                       password=STOCK_PASSWORD)
        self.user = User.objects.get(username='user')

    def test_login(self):
        self.assertTrue(self.login)

    def test_switch_permissions(self):
        settings.RESTRICT_PACKAGE_EDITORS = False
        response = self.client.get(self.test_add_url)
        self.assertEqual(response.status_code, 200)
        settings.RESTRICT_PACKAGE_EDITORS = True
        response = self.client.get(self.test_add_url)
        self.assertEqual(response.status_code, 403)

    @override_settings(RESTRICT_PACKAGE_EDITORS=True)
    def test_add_package_permission_fail(self):
        response = self.client.get(self.test_add_url)
        self.assertEqual(response.status_code, 403)

    def test_add_package_permission_success(self):
        add_package_perm = Permission.objects.get(
            codename="add_package",
            content_type__app_label='package'
        )
        self.user.user_permissions.add(add_package_perm)
        response = self.client.get(self.test_add_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_package_permission_fail(self):
        response = self.client.get(self.test_edit_url)
        self.assertEqual(response.status_code, 403)

    def test_edit_package_permission_success(self):
        edit_package_perm = Permission.objects.get(
            codename="change_package",
            content_type__app_label='package')
        self.user.user_permissions.add(edit_package_perm)
        response = self.client.get(self.test_edit_url)
        self.assertEqual(response.status_code, 200)
