# encoding: utf-8

import os
import tempfile

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

    def open_sample_image(self):
        """Convenience method to return an open Image"""
        sample_jpg = os.path.join(SAMPLE_DIR, "5071384885_c5f331d337_b.jpg")
        return self.IMAGE_CLASS.open(sample_jpg)

    def test_size(self):
        self.assertEqual(self.open_sample_image().size, (1024L, 680L))

    def test_repr(self):
        self.assertNotEqual(0, len(repr(self.open_sample_image())))

    def test_save(self):
        """Test of basic image saving"""
        img = self.open_sample_image()
        img.save(tempfile.TemporaryFile(), format="PNG")

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
        self.assertEqual(img.size, (128L, 85L))

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
        self.assertEqual( _info(self.IMAGE_CLASS.new("RGB", (128, 128))), (None, 'RGB', (128, 128)))

        # 32-bit integer
        self.assertEqual(_info(self.IMAGE_CLASS.new("I", (128, 128))), (None, 'I', (128, 128)))

        # 32-bit floating point
        self.assertEqual(_info(self.IMAGE_CLASS.new("F", (128, 128))), (None, 'F', (128, 128)))

    def test_crop(self):
        img = self.open_sample_image()
        self.assertEqual(img.crop((32, 32, 96, 96)).size, (64, 64))

    def test_rotate(self):
        img = self.open_sample_image()
        self.assertEqual(img.rotate(45).size, (1024L, 680L))
