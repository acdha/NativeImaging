# encoding: utf-8

import os

SAMPLE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "samples"))

class ApiConformanceTests(object):
    """
    API conformance tests

    Subclasses *must* inherit from both this and TestCase
    Subclasses *must* define self.IMAGE_CLASS
    """

    def test_open(self):
        sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")

        # Accepts filenames:
        img = self.IMAGE_CLASS.open(sample_jpg)
        self.assertTrue(img)

        self.assertRaises(IOError, self.IMAGE_CLASS.open, "this test image does not exist.jpg")

        # Accepts file objects:
        img = self.IMAGE_CLASS.open(file(sample_jpg))
        self.assertTrue(img)

        # … and file-like objects:
        from StringIO import StringIO
        img = self.IMAGE_CLASS.open(StringIO(file(sample_jpg).read()))
        self.assertTrue(img)

    def test_size(self):
        sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")

        # Accepts filenames:
        img = self.IMAGE_CLASS.open(sample_jpg)
        self.assertEqual(img.size, (1024L, 680L))

    def test_resize(self):
        sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")

        # Accepts filenames:
        img = self.IMAGE_CLASS.open(sample_jpg)

        small = img.resize((128, 256))

        self.assertNotEqual(img, small)
        self.assertNotEqual(img.size, small.size)

        # Confirm that width & height were modified correctly: unlike
        # thumbnail, resize should stretch:
        self.assertEqual(small.size, (128, 256))

    def test_thumbnail(self):
        sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")

        # Accepts filenames:
        img = self.IMAGE_CLASS.open(sample_jpg)

        # Thumbnail is an in-place modification:
        self.assertEqual(img.thumbnail((128, 256)), None)

        # Confirm that width & height were modified correctly: unlike
        # resize the image shouldn't be stretched so only one of our provided
        # values will be the same:
        self.assertEqual(img.size, (128L, 85L))
