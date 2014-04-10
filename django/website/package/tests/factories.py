from factory import SubFactory
from factory.django import DjangoModelFactory

from package.models import Package, Format, Category


class CategoryFactory(DjangoModelFactory):
    FACTORY_FOR = Category


class FormatFactory(DjangoModelFactory):
    FACTORY_FOR = Format


class DatasetFactory(DjangoModelFactory):
    """
    Note a package is a dataset, slowly moving to new names
    """
    FACTORY_FOR = Package

    category = SubFactory(CategoryFactory)
    machine_readable = False
