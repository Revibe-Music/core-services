"""
Test the content utils functions

Created: 17 Feb. 2020
Author: Jordan Prechac
"""

from django.test import TestCase

from content.models import Tag
from content.utils.models import get_tag

# -----------------------------------------------------------------------------

class ModelsTestCase(TestCase):

    def test_get_tag_doesnt_exist(self):
        """
        """
        tag = get_tag("Funky")

        self.assertEqual(
            tag, Tag.objects.get(text="Funky"),
            msg="The correct tag was not found"
        )

    def test_get_tag_does_exist(self):
        # create test tag
        Tag.objects.create(text="Testy")

        # retrieve the tag with get_tag
        tag = get_tag("Testy")

        # ensure that the function got the correct tag
        self.assertEqual(
            tag, Tag.objects.get(text="Testy"),
            msg="The correct tag was not found or was not created"
        )

