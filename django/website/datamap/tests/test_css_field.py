from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from needle.cases import NeedleTestCase
from .factories import DatamapFactory


class AddFieldViewCSSTest(NeedleTestCase, LiveServerTestCase):
    pass # Because I was told

    # def test_form(self):
    #     datamap = DatamapFactory()
    #     url = reverse('datamap_field_add', kwargs={'dm': datamap.id})
    #     self.driver.get("%s%s" % (self.live_server_url, url))
    #     self.assertScreenshot('.datamap-field-edit-form', 'datamap-field-form')
