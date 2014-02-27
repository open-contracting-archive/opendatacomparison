from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField

from core.models import BaseModel


class Publisher(BaseModel):

    name = models.CharField(_('Title'), max_length='50')
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)
    country = CountryField(blank=True)
    url = models.URLField(_('website'), blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.country, self.name)
