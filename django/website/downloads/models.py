from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import (
    ForeignKey,
    URLField,
    TextField,
    DateTimeField,
    CharField,
)
from core.models import BaseModel
from package.models import Package, Format


class Link(BaseModel):
    dataset = ForeignKey(Package, related_name='downloads')
    title = CharField(max_length=100)
    url = URLField()
    format = ForeignKey(Format)
    notes = TextField(blank=True)

    class Meta:
        ordering = '?'

    def __unicode__(self):
        return '%s - %s (%s)' % (self.format, self.title, self.dataset)

    def record_click(self, session_key, username):
        click = Click.objects.create(link=self,
                                     session_key=session_key,
                                     username=username)
        return click

    def get_absolute_url(self):
        return reverse('download', args=[str(self.id)])

    def get_fully_qualified_url(self):
        site = Site.objects.get_current()
        return 'http://%s%s' % (site.domain, self.get_absolute_url())


class Click(BaseModel):
    link = ForeignKey(Link)
    time = DateTimeField(auto_now_add=True)
    session_key = CharField(max_length=64, default='default')
    username = CharField(max_length=64, default='default')
