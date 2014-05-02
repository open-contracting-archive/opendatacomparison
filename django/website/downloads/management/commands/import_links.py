from __future__ import unicode_literals
import os
import csv

from django.core.management.base import BaseCommand, CommandError

from downloads.models import Link, Click


def unicode_dict_reader(utf8_data, **kwargs):
        csv_reader = csv.DictReader(utf8_data, **kwargs)
        for row in csv_reader:
            yield dict((key, unicode(value, 'utf-8'))
                       for key, value in row.iteritems())


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
                    self.insert_row(row_dict)
                    self.num_rows_added += 1

        self.stdout.write("Number of CSV rows parsed and added: %s"
                          % self.num_rows_added)

    def insert_row(self, row_dict):
        print 'do something'
