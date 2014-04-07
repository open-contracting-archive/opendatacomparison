from django.test import TestCase

from package.models import Package, Version
from package.tests.data import PackageTestCase


class VersionTests(PackageTestCase):
    def test_version_order(self):
        p = Package.objects.get(slug='django-cms')
        versions = p.version_set.by_version()
        expected_values = ['2.0.0',
                           '2.0.1',
                           '2.0.2',
                           '2.1.0',
                           '2.1.0.beta3',
                           '2.1.0.rc1',
                           '2.1.0.rc2',
                           '2.1.0.rc3',
                           '2.1.1',
                           '2.1.2',
                           '2.1.3']
        returned_values = [v.number for v in versions]
        self.assertEquals(returned_values, expected_values)

    def test_version_license_length(self):
        v = Version.objects.all()[0]
        v.license = "x" * 50
        v.save()
        self.assertEquals(v.license, "Custom")
