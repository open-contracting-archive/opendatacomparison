from __future__ import unicode_literals
from django.test import TestCase

from .factories import ConceptFactory


class TestConceptModel(TestCase):

    def test_unicode_returns_string(self):
        concept = ConceptFactory(name='my concept')
        self.assertEqual(concept.__unicode__(), 'my concept')
