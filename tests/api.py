# encoding: utf-8

from __future__ import absolute_import, division, print_function

import os
import tempfile
from io import BytesIO

SAMPLE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "samples"))


class ApiConformanceTests(object):
    """
    API conformance tests

    Subclasses *must* inherit from both this and TestCase
    Subclasses *must* define self.IMAGE_CLASS
    """

    def setUp(self):
        super(ApiConformanceTests, self).setUp()

        self.sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")

    def test_open_filename(self):
        # Accepts filenames:
        img = self.IMAGE_CLASS.open(self.sample_jpg)
        self.assertTrue(img)

        self.assertRaises(IOError, self.IMAGE_CLASS.open, "this test image does not exist.jpg")

    def test_open_file_pointer(self):
        with open(self.sample_jpg, 'rb') as f:
            img = self.IMAGE_CLASS.open(f)
        self.assertTrue(img)

    def test_open_filelike_objects(self):
        with open(self.sample_jpg, 'rb') as f:
            bytes_io = BytesIO(f.read())
        img = self.IMAGE_CLASS.open(bytes_io)
        self.assertTrue(img)

    def open_sample_image(self):
        """Convenience method to return an open Image"""
        return self.IMAGE_CLASS.open(self.sample_jpg)

    def test_save_as_jpeg(self):
        """Test of basic image saving"""
        img = self.open_sample_image()
        with tempfile.TemporaryFile() as f:
            img.save(f, format="JPEG")

    def test_save_with_quality(self):
        """Test of basic image saving"""
        img = self.open_sample_image()
        with tempfile.TemporaryFile() as f:
            img.save(f, format="JPEG", quality=75)

    def test_size(self):
        self.assertEqual(self.open_sample_image().size, (1024, 680))

    def test_repr(self):
        self.assertNotEqual(0, len(repr(self.open_sample_image())))

    def test_save_as_png(self):
        """Test of basic image saving"""
        img = self.open_sample_image()
        with tempfile.TemporaryFile() as f:
            img.save(f, format="PNG")

    def test_resize(self):
        img = self.open_sample_image()
        small = img.resize((128, 256))

        self.assertNotEqual(img, small)
        self.assertNotEqual(img.size, small.size)

        # Confirm that width & height were modified correctly: unlike
        # thumbnail, resize should stretch:
        self.assertEqual(small.size, (128, 256))

    def test_thumbnail(self):
        img = self.open_sample_image()

        # Thumbnail is an in-place modification:
        self.assertEqual(img.thumbnail((128, 256)), None)

        # Confirm that width & height were modified correctly: unlike
        # resize the image shouldn't be stretched so only one of our provided
        # values will be the same:
        self.assertEqual(img.size, (128, 85))

    def disabled_new_image(self):
        # TODO: Implement Image.new and enable this test
        # Converted from PIL doc tests:
        def _info(img):
            return img.format, img.mode, img.size

        # monochrome
        self.assertEqual(_info(self.IMAGE_CLASS.new("1", (128, 128))), (None, '1', (128, 128)))

        # grayscale (luminance)
        self.assertEqual(_info(self.IMAGE_CLASS.new("L", (128, 128))), (None, 'L', (128, 128)))

        # palette
        self.assertEqual(_info(self.IMAGE_CLASS.new("P", (128, 128))), (None, 'P', (128, 128)))

        # truecolor
        self.assertEqual(_info(self.IMAGE_CLASS.new("RGB", (128, 128))), (None, 'RGB', (128, 128)))

        # 32-bit integer
        self.assertEqual(_info(self.IMAGE_CLASS.new("I", (128, 128))), (None, 'I', (128, 128)))

        # 32-bit floating point
        self.assertEqual(_info(self.IMAGE_CLASS.new("F", (128, 128))), (None, 'F', (128, 128)))

    def test_crop(self):
        img = self.open_sample_image()
        self.assertEqual(img.crop((32, 32, 96, 96)).size, (64, 64))

    def test_rotate_90(self):
        img = self.open_sample_image()
        self.assertEqual(img.size, (1024, 680))

        self.assertEqual(img.rotate(90).size, (1024, 680))
        self.assertEqual(img.rotate(90, expand=True).size, (680, 1024))

    def test_rotate_arb(self):
        img = self.open_sample_image()
        self.assertEqual(img.size, (1024, 680))
        self.assertEqual(img.rotate(43).size, (1024, 680))
