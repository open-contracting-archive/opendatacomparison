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
    dataset = ForeignKey(Package)
    title = CharField(max_length=100)
    link = URLField()
    format = ForeignKey(Format)
    notes = TextField(blank=True)

    def __unicode__(self):
        return self.title


class Click(BaseModel):
    link = ForeignKey(Link)
    time = DateTimeField(auto_now_add=True)
