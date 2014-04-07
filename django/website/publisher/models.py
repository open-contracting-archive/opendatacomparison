from django.db.models import (
    CharField,
    SlugField,
    TextField,
    IntegerField,
    URLField,
)
from django.utils.translation import ugettext_lazy as _

from international.models import countries

from core.models import BaseModel


class Publisher(BaseModel):

    name = CharField(_('Title'), max_length=50)
    slug = SlugField(_('Slug'), unique=True)
    description = TextField(_('Description'), blank=True)
    country = CharField(
        _('Country'),
        max_length=2,
        choices=countries,
        blank=True)
    url = URLField(_('Website'), blank=True)
    administrative_level = CharField(
        _('Administrative Level'),
        max_length=100,
        help_text='What level is this dataset on (Provincial, State, County)? \
        Use the term appropriate for the dataset is in e.g. if its Canadian, \
        use Province, if USA use State',
        blank=True
    )
    administrative_cat = IntegerField(
        _('Adminitrative Level Category'),
        help_text="""See the wikipedia page
        https://en.wikipedia.org/wiki/Table_of_administrative_divisions_by_country
        and select the appropriate level for the
        datasets administrative level.)""",
        choices=((-1, 'International'),
                 (0, 'National'),
                 (1, 'First-level'),
                 (2, 'Second-level'),
                 (3, 'Third-level'),
                 (4, 'Fourth-level and smaller')),
        blank=True,
        null=True,
    )

    def country_name(self):
        dc = dict(countries)
        return dc.get(self.country)

    def __unicode__(self):
        return u'%s - %s' % (self.country, self.name)
