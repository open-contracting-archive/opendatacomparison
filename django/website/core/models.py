from __future__ import unicode_literals
import json
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _
from django.core.mail import mail_managers
import reversion

from core.fields import CreationDateTimeField, ModificationDateTimeField


class BaseModel(models.Model):
    """ Base abstract base class to give creation and modified times """
    created = CreationDateTimeField(_('created'))
    modified = ModificationDateTimeField(_('modified'))

    class Meta:
        abstract = True

    def cache_namer(self, method):
        return "{}:{}".format(
            method.__name__,
            self.pk
        )

    def model_cache_name(self):
        return "{}:{}".format(
            self.__class__.__name__,
            self.pk
        )


def on_revision_commit(instances, **kwargs):
    revision = kwargs.get('revision')
    subject = '[ocds changes] %s made a change' % revision.user.username
    message = ''
    versions = kwargs.get('versions')
    for version in versions:
        message += '%s was changed to:\n' % version.object_repr
        message += json.dumps(version.field_dict,
                              indent=True,
                              cls=DjangoJSONEncoder)
        message += '\n\n\n'
    mail_managers(subject, message)

reversion.post_revision_commit.connect(on_revision_commit)
