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
    dataset = ForeignKey(Package, related_name='datamaps')
    notes = TextField(_('Notes'), null=True, blank=True)
    format = ForeignKey(Format)

    def __unicode__(self):
        return u'%s - %s' % (self.dataset, self.format)


class Concept(BaseModel):
    name = CharField(_('Name'), max_length=100)
    description = TextField(_('Description'), blank=True)
    parent = ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        if self.parent:
            return u'%s - %s' % (self.parent, self.name)
        else:
            return u'%s' % self.name

    class Meta:
        unique_together = ("parent", "name")


class Field(BaseModel):
    datamap = ForeignKey(Datamap, related_name='fields')
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

    def __unicode__(self):
        return u'%s: %s' % (self.datamap, self.fieldname)


class TranslatedField(BaseModel):
    field = ForeignKey(Field, related_name='translations')
    language = CharField(_('Language'),
                         max_length=10,
                         choices=languages,
                         default='en_US')
    title = CharField(_('Title'), max_length=100)
    description = TextField(_('Description'), blank=True)
    allowable_values = TextField(_('Allowable values'), blank=True)

    def language_name(self):
        dc = dict(languages)
        return dc.get(self.language)
