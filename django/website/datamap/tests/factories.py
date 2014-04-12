# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from factory import SubFactory
from factory.django import DjangoModelFactory

from package.tests.factories import FormatFactory, DatasetFactory

from datamap.models import Datamap, Field, TranslatedField


class DatamapFactory(DjangoModelFactory):
    FACTORY_FOR = Datamap

    dataset = SubFactory(DatasetFactory)
    format = SubFactory(FormatFactory)


class DatafieldFactory(DjangoModelFactory):
    FACTORY_FOR = Field

    datamap = SubFactory(DatamapFactory)


class TranslatedFieldFactory(DjangoModelFactory):
    FACTORY_FOR = TranslatedField

    field = SubFactory(DatafieldFactory)
    title = 'Ⓣⓨⓟⓔ ⓨⓞⓤⓡ ⓣⓔⓧⓣ ⓗⓔⓡⓔ    '
