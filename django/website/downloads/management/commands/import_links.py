from __future__ import unicode_literals
import os
import csv

from django.core.management.base import BaseCommand, CommandError

from downloads.models import Link
from package.models import Format, Package


def unicode_dict_reader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield dict((key, unicode(value, 'utf-8'))
                   for key, value in row.iteritems())


file_format_dictionary = {
    'Link-API': 'API',
    'Link-Website': 'Website',
    'Link-PDF': 'PDF',
    'Link-RSS': 'RSS',
    'Link-XLSX': 'Excel',
    'Link-XLS': 'Excel',
    'Link-XML': 'XML',
    'Link-JSON': 'JSON',
    'Link-CSV': 'CSV',
    'Link-ODS': 'ODS',
    'Link-RDF': 'RDF',
    'Link-ZIP': 'ZIP',
}


def get_format(format_key):
    try:
        title = file_format_dictionary.get(format_key)
        format = Format.objects.get(title=title)
    except:
        raise CommandError('Format not found for %s' % format_key)
    return format


def get_dataset(slug):
    try:
        dataset = Package.objects.get(slug=slug)
    except:
        raise CommandError('Dataset not found for %s' % slug)
    return dataset


def insert_row(row_dict):
    print row_dict
    format_keys = [key for key in row_dict.keys()
                   if
                   key.startswith('Link-')
                   and
                   row_dict.get(key).strip() is not '']
    for f in format_keys:
        link = Link(dataset=get_dataset(row_dict.get('Slug')),
                    title=row_dict.get('Link Name', 'None provided'),
                    url=row_dict.get(f),
                    format=get_format(f),
                    notes=row_dict.get('Notes'))
        link.save()


class Command(BaseCommand):
    args = '<csv_path>'
    help = 'Parses a datamap CSV and adds it to the database'

    num_rows_added = 0

    def handle(self, *args, **options):
        if not len(args) == 1:
            raise CommandError('Incorrect number of arguments.')

        csv_path = args[0]

        if not os.path.isfile(csv_path):
            raise CommandError('CSV file path invalid.')

        with open(csv_path, 'r') as csv_file:
            try:
                reader = unicode_dict_reader(csv_file)
            except Exception as e:
                raise CommandError('Unable to create CSV parser. Error %s' % e)

            if reader:
                for row_dict in reader:
                    insert_row(row_dict)
                    self.num_rows_added += 1

        self.stdout.write("Number of CSV rows parsed and added: %s"
                          % self.num_rows_added)

