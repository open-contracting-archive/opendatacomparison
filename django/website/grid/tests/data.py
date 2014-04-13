from django.contrib.auth.models import Group, User, Permission

from core.tests.data import OpenComparisonTestCase
from grid.models import Grid
from grid.models import Element, Feature, GridPackage
from package.models import Category, Package


class GridTestCase(OpenComparisonTestCase):
    def setUp(self):
        super(GridTestCase, self).setUp()

        grid1, created = Grid.objects.get_or_create(
            description=u'A grid for testing.',
            title=u'Testing',
            is_locked=False,
            slug=u'testing',
        )
        grid2, created = Grid.objects.get_or_create(
            description=u'Another grid for testing.',
            title=u'Another Testing',
            is_locked=False,
            slug=u'another-testing',
        )

        self.gridpackage1, created = GridPackage.objects.get_or_create(
            package=Package.objects.get(slug='testability'),
            grid=grid1,
        )
        self.gridpackage2, created = GridPackage.objects.get_or_create(
            package=Package.objects.get(slug='supertester'),
            grid=grid1,
        )
        self.gridpackage3, created = GridPackage.objects.get_or_create(
            package=Package.objects.get(slug='serious-testing'),
            grid=grid1,
        )
        self.gridpackage4, created = GridPackage.objects.get_or_create(
            package=Package.objects.get(slug='another-test'),
            grid=grid2,
        )
        self.gridpackage5, created = GridPackage.objects.get_or_create(
            package=Package.objects.get(slug='supertester'),
            grid=grid1,
        )
        self.feature1, created = Feature.objects.get_or_create(
            title=u'Has tests?',
            grid=grid1,
            description=u'Does this package come with tests?',
        )
        Feature.objects.get_or_create(
            title=u'Coolness?',
            grid=grid1,
            description=u'Is this package cool?',
        )

        element, created = Element.objects.get_or_create(
            text=u'Yes',
            feature=self.feature1,
            grid_package=self.gridpackage1,
        )

        group1, created = Group.objects.get_or_create(
            name=u'Moderators',
        )
        group1.permissions.clear()
        group1.permissions = [
            Permission.objects.get(codename='delete_gridpackage'),
            Permission.objects.get(codename='delete_feature')
        ]
        cleaner_user = User.objects.get(username='cleaner')
        cleaner_user.groups = [group1]
        cleaner_user.save()
