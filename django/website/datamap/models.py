from django.utils.translation import ugettext_lazy as _
from django.db.models import (
    CharField,
    TextField,
    ForeignKey,
)
from package.models import Package
from core.models import BaseModel
from international.models import languages


class Field(BaseModel):
    dataset = ForeignKey(Package)
    fieldname = CharField(_('Field Name'), max_length=100)
    datatype = CharField(_('Type'),
                         max_length=30,
                         choices=(
                             ('Boolean', _('Yes/No')),
                             ('Number', _('Number')),
                             ('Currency', _('Currency Value')),
                             ('DateTime', _('Date or DateTime')),
                             ('Text', _('Free Text')),
                             ('SingleSelect', _('Single Select')),
                             ('MultiSelect', _('MultiSelect')),
                         ))


class TranslatedField(BaseModel):
    field = ForeignKey(Field)
    language = CharField(_('Language'),
                         max_length=10,
                         choices=languages,
                         default='en_US')
    title = CharField(_('Title'), max_length=100)
    description = TextField(_('Description'))
    allowable_values = TextField(_('Allowable values'), blank=True)
