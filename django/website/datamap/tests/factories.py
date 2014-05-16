# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from factory import SubFactory
from factory.django import DjangoModelFactory

from package.tests.factories import (
    FormatFactory,
    DatasetFactory,
    DatasetWithPublisherFactory,
)

from datamap.models import Datamap, Field, TranslatedField, Concept


class DatamapFactory(DjangoModelFactory):
    FACTORY_FOR = Datamap

    dataset = SubFactory(DatasetFactory)
    format = SubFactory(FormatFactory)


class DatamapWithPublisherFactory(DjangoModelFactory):
    FACTORY_FOR = Datamap

    dataset = SubFactory(DatasetWithPublisherFactory)
    format = SubFactory(FormatFactory)


class ConceptFactory(DjangoModelFactory):
    FACTORY_FOR = Concept


class DatafieldFactory(DjangoModelFactory):
    FACTORY_FOR = Field

    datamap = SubFactory(DatamapFactory)
    concept = SubFactory(ConceptFactory)
    fieldname = 'fieldname'
    datatype = 'Boolean'


class TranslatedFieldFactory(DjangoModelFactory):
    FACTORY_FOR = TranslatedField

    field = SubFactory(DatafieldFactory)
    title = 'Ⓣⓨⓟⓔ ⓨⓞⓤⓡ ⓣⓔⓧⓣ ⓗⓔⓡⓔ    '
