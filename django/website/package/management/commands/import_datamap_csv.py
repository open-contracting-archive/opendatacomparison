from __future__ import unicode_literals
from datamap.models import Field, Concept, TranslatedField, Datamap

import os
import csv

from django.core.management.base import BaseCommand, CommandError


def unicode_dict_reader(utf8_data, **kwargs):
        csv_reader = csv.DictReader(utf8_data, **kwargs)
        for row in csv_reader:
            yield dict((key, unicode(value, 'utf-8')) for key, value in row.iteritems())


class Command(BaseCommand):
    args = '<datamap_id> <csv_path>'
    help = 'Parses a datamap CSV and adds it to the database'

    required_keys = set([
        'original_name',
        'data_type',
    ])

    datamap = None

    num_rows_added = 0

    def handle(self, *args, **options):
        if not len(args) == 2:
            raise CommandError('Incorrect number of arguments.')

        datamap_id = args[0]
        csv_path = args[1]

        self.datamap = Datamap.objects.get(id=datamap_id)

        if not self.datamap:
            raise CommandError('Invalid datamap id.')

        if not os.path.isfile(csv_path):
            raise CommandError('CSV file path invalid.')

        with open(csv_path, 'r') as csv_file:
            try:
                reader = unicode_dict_reader(csv_file)
            except Exception as e:
                raise CommandError('Unable to create CSV parser. Error: ' + str(e))

            if reader:
                for row_dict in reader:
                    self.insert_row(row_dict)
                    self.num_rows_added += 1

        self.stdout.write("Number of CSV rows parsed and added: %s" % self.num_rows_added)

    def insert_row(self, row_dict):
        if not self.check_required_keys(row_dict.keys()):
            raise CommandError("CSV is missing required keys.")

        phase = row_dict.get('phase', None)  # not required
        entity = row_dict.get('entity', None)  # not required
        concept_name = "_".join([item for item in (phase.capitalize(), entity.capitalize()) if item])

        concept, created = Concept.objects.get_or_create(phase=phase, entity=entity)

        concept.name = concept_name
        concept.phase = phase
        concept.entity = entity
        concept.save()

        original_name = row_dict.get('original_name')
        field, created = Field.objects.get_or_create(datamap=self.datamap, fieldname=original_name)
        field.fieldname = original_name  # required
        field.formattedname = row_dict.get('formatted_name', '')  # not required
        field.standardname = row_dict.get('standard_name', '')  # not required
        field.concept = concept
        field.datatype = row_dict.get('data_type')  # required
        field.save()

        trans_langs_keys = self.detect_translated_languages_and_keys(row_dict.keys())
        for language, keys in trans_langs_keys.iteritems():
            trans_field, created = TranslatedField.objects.get_or_create(field=field, language=language)

            for key_name, orig_key in keys:
                if key_name == 'title':
                    trans_field.title = row_dict[orig_key]
                elif key_name == 'description':
                    trans_field.description = row_dict[orig_key]
                elif key_name == 'allowable_values':
                    trans_field.allowable_values = row_dict[orig_key]

            trans_field.save()

    def detect_translated_languages_and_keys(self, keys):
        trans_langs_keys = {}

        # attempt to split languages off of key names
        # format as somekeyname__en_US
        for key in keys:
            key_components = key.split('__')
            if len(key_components) > 1:
                lang_string = key_components[-1]
                if not lang_string in trans_langs_keys:
                    trans_langs_keys[lang_string] = set([])

                trans_langs_keys[lang_string].add((key_components[0], key))

        # returns {'en_US': ('keyname', 'keyname__en_US'))}
        return trans_langs_keys

    def check_required_keys(self, keys):
        return set(keys).issuperset(self.required_keys)
