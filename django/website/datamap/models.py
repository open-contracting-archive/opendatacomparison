from django.utils.translation import ugettext_lazy as _
from django.db.models import (
    CharField,
    TextField,
    ForeignKey,
    ManyToManyField,
)
from package.models import Package, Format
from core.models import BaseModel
from international.models import languages


class Datamap(BaseModel):
    dataset = ForeignKey(Package)
    notes = TextField(_('Notes'), null=True, blank=True)
    format = ForeignKey(Format)

    def __unicode__(self):
        return '%s - $s' % (self.dataset, self.format)


class Concept(BaseModel):
    name = CharField(_('Name'), max_length=100, unique=True)
    description = TextField(_('Description'))
    parent = ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        if self.parent:
            return '%s - $s' % (self.parent, self.name)
        else:
            return self.name


class Field(BaseModel):
    datamap = ForeignKey(Datamap)
    fieldname = CharField(_('Field Name'), max_length=100)
    concept = ForeignKey(Concept, null=True, blank=True)
    mapsto = ManyToManyField('self', null=True, blank=True)
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

    class Meta:
        unique_together = ('datamap', 'fieldname')


class TranslatedField(BaseModel):
    field = ForeignKey(Field)
    language = CharField(_('Language'),
                         max_length=10,
                         choices=languages,
                         default='en_US')
    title = CharField(_('Title'), max_length=100)
    description = TextField(_('Description'))
    allowable_values = TextField(_('Allowable values'), blank=True)
