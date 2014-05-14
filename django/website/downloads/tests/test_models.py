from django.test import TestCase

from downloads.models import Click
from .factories import LinkFactory


class TestRecordClick(TestCase):

    def test_record_click_adds_a_new_click_to_db(self):
        count = Click.objects.count()
        link = LinkFactory()
        link.record_click(session_key='test',
                          username='anonymous')
        self.assertEqual(Click.objects.count(), count + 1)

    def test_record_click_sets_timestamps_on_each_click(self):
        """
        Test that a session key is set to the value passed in (can
        assume that datetime is saved as can assume django is working).
        """
        link = LinkFactory()
        click = link.record_click(session_key='test',
                                  username='anonymous')
        self.assertEqual(click.session_key, 'test')
        self.assertEqual(click.username, 'anonymous')
