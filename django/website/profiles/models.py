from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User)
    url = models.URLField(_('Website'), null=True, blank=True)

    def __unicode__(self):
        return self.user

    def my_packages(self):
        """Return a list of all packages the user contributes to.

        List is sorted by package name.
        """
        from package.repos import get_repo, supported_repos

        packages = []
        for repo in supported_repos():
            repo = get_repo(repo)
            repo_packages = repo.packages_for_profile(self)
            packages.extend(repo_packages)
        packages.sort(lambda a, b: cmp(a.title, b.title))
        return packages

    @property
    def can_add_package(self):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            return self.user.has_perm('package.add_package')
        # anyone can add
        return True

    @property
    def can_edit_package(self):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            # this is inconsistent, fix later?
            return self.user.has_perm('package.change_package')
        # anyone can edit
        return True

    # Grids
    @property
    def can_edit_grid(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.change_grid')
        return True

    @property
    def can_add_grid(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.add_grid')
        return True

    # Grid Features
    @property
    def can_add_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.add_feature')
        return True

    @property
    def can_edit_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.change_feature')
        return True

    @property
    def can_delete_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.delete_feature')
        return True

    # Grid Packages
    @property
    def can_add_grid_package(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.add_gridpackage')
        return True

    @property
    def can_delete_grid_package(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.delete_gridpackage')
        return True

    # Grid Element (cells in grid)
    @property
    def can_edit_grid_element(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self.user.has_perm('grid.change_element')
        return True
