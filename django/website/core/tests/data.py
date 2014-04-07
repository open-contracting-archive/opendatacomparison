from django.contrib.auth.models import User
from django.test import TestCase

from package.models import Category, Package

STOCK_PASSWORD = "stock_password"


class OpenComparisonTestCase(TestCase):

    def setUp(self):
        self.make()

    def make(self):
        self.create_users()
        self.category, created = Category.objects.get_or_create(
            title="App",
            slug="apps",
            description="Small components used to build projects."
        )
        package, created = Package.objects.get_or_create(
            category=self.category,
            description="Increase your testing ability with this steroid free supplement.",  # nopep8
            url="https://github.com/pydanny/django-la-facebook",
            slug="testability",
            title="Testability",
            machine_readable=False,
        )
        package, created = Package.objects.get_or_create(
            category=self.category,
            description="Test everything under the sun with one command!",
            url="https://github.com/pydanny/django-uni-form",
            slug="supertester",
            title="Supertester",
            machine_readable=False,
        )
        package, created = Package.objects.get_or_create(
            category=self.category,
            description="Make testing as painless as frozen yogurt.",
            url="https://github.com/opencomparison/opencomparison",
            slug="serious-testing",
            title="Serious Testing",
            machine_readable=False,
        )
        package, created = Package.objects.get_or_create(
            category=self.category,
            description="Yet another test package, with no grid affiliation.",  # nopep8
            url="https://github.com/djangopackages/djangopackages",
            slug="another-test",
            title="Another Test",
            machine_readable=False,
        )

    def create_users(self):

        user = User.objects.create_user(
            username="user",
            password=STOCK_PASSWORD,
            email="user@example.com"
        )
        user.is_active = True
        user.save()

        user = User.objects.create_user(
            username="cleaner",
            password="cleaner",
            email="cleaner@example.com"
        )
        user.is_active = True
        user.save()

        user = User.objects.create_user(
            username="staff",
            password="staff",
            email="staff@example.com"
        )
        user.is_active = True
        user.is_staff = True
        user.save()

        user = User.objects.create_user(
            username="admin",
            password="admin",
            email="admin@example.com"
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
