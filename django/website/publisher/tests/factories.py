from factory import Sequence
from factory.django import DjangoModelFactory

from publisher.models import Publisher


class PublisherFactory(DjangoModelFactory):
    FACTORY_FOR = Publisher

    country = 'en'
    slug = Sequence(lambda n: 'slug{0}'.format(n))
