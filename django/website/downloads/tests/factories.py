from factory import SubFactory, Sequence
from factory.django import DjangoModelFactory

from downloads.models import Link
from package.tests.factories import DatasetFactory, FormatFactory


class LinkFactory(DjangoModelFactory):
    FACTORY_FOR = Link

    title = Sequence(lambda n: 'link title {0}'.format(n))
    dataset = SubFactory(DatasetFactory)
    format = SubFactory(FormatFactory)
