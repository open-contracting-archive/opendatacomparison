from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, related_name='profile')
    url = models.URLField(_('Website'), null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.user

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

    # Datamaps
    @property
    def can_edit_datamap(self):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            return self.user.has_perm('datamap.change_datamap')
        return True

    @property
    def can_add_datamap(self):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            return self.user.has_perm('datamap.add_datamap')
        return True


def slugify_username(sender, instance, **kwargs):
    instance.username = slugify(instance.username)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

pre_save.connect(slugify_username, sender=User)
post_save.connect(create_user_profile, sender=User)
