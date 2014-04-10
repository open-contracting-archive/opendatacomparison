from factory import SubFactory
from factory.django import DjangoModelFactory

from package.tests.factories import DatasetFactory, FormatFactory

from datamap.models import Datamap


class DatamapFactory(DjangoModelFactory):
    FACTORY_FOR = Datamap

    dataset = SubFactory(DatasetFactory)
    format = SubFactory(FormatFactory)