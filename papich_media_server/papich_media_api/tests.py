from django.test import TestCase
from .models import MediaContent


class MediaContentTestCase(TestCase):
    def setUp(self):
        MediaContent.objects.create(displayed_name="sample", filepath="sample/filepath/to/file.mp3")

    def test_get_media_content(self):
        sample_content = MediaContent.objects.get(displayed_name="sample")
        self.assertEqual(sample_content.filepath, "sample/filepath/to/file.mp3")
