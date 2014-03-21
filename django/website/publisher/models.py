from django.db.models import (
    CharField,
    SlugField,
    TextField,
    URLField,
)
from django.utils.translation import ugettext_lazy as _

from international.models import countries

from core.models import BaseModel


class Publisher(BaseModel):

    name = CharField(_('Title'), max_length=50)
    slug = SlugField(_('Slug'), unique=True)
    description = TextField(_('Description'), blank=True)
    country = CharField(_('Country'),
                            max_length=2,
                            choices=countries,
                            blank=True)
    url = URLField(_('Website'), blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.country, self.name)
