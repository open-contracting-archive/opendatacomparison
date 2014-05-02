from __future__ import unicode_literals
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

    def __unicode__(self):
        return self.title

    def record_click(self, session_key, username):
        click = Click.objects.create(link=self,
                                     session_key=session_key,
                                     username=username)
        return click


class Click(BaseModel):
    link = ForeignKey(Link)
    time = DateTimeField(auto_now_add=True)
    session_key = CharField(max_length=64, default='default')
    username = CharField(max_length=64, default='default')
