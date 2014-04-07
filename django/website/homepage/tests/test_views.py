from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from core.tests.data import OpenComparisonTestCase
from grid.tests.data import GridTestCase
from grid.models import Grid
from homepage.models import Dpotw, Gotw
from package.models import Package, Category

from homepage.views import error_500_view


class FunctionalHomepageTest(GridTestCase):

    def test_homepage_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        for p in Package.objects.all():
            self.assertContains(response, p.title)
            self.assertContains(response, p.description)

        self.assertEquals(response.context['package_count'],
                          Package.objects.count())

    def test_packages_on_homepage(self):
        """
        Latest packages should be listed on the homepage
        """
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')

        for p in Package.objects.all():
            self.assertContains(response, p.title)
            self.assertContains(response, p.description)

    def test_items_of_the_week(self):
        url = reverse('home')
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        p = Package.objects.all()[0]
        g = Grid.objects.all()[0]

        d_live = Dpotw.objects.create(package=p,
                                      start_date=yesterday,
                                      end_date=tomorrow)

        g_live = Gotw.objects.create(grid=g,
                                     start_date=yesterday,
                                     end_date=tomorrow)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')
        self.assertContains(response, d_live.package.title)
        self.assertContains(response, g_live.grid.title)


class FunctionalHomepageTestWithoutPackages(OpenComparisonTestCase):

    def test_homepage_view(self):
        Package.objects.all().delete()
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'homepage.html')


class TestErrorPages(TestCase):

    def test_404_test(self):
        r = self.client.get("/404")
        self.assertEquals(r.status_code, 404)

    def test_500_test(self):
        r = error_500_view(RequestFactory().get('/'))
        self.assertEquals(r.status_code, 500)
