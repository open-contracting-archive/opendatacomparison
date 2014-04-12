from factory import SubFactory
from factory.django import DjangoModelFactory

from package.tests.factories import FormatFactory, DatasetFactory

from datamap.models import Datamap, Field


class DatamapFactory(DjangoModelFactory):
    FACTORY_FOR = Datamap

    dataset = SubFactory(DatasetFactory)
    format = SubFactory(FormatFactory)


class DatafieldFactory(DjangoModelFactory):
    FACTORY_FOR = Field

    datamap = SubFactory(DatamapFactory)
