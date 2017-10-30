#!/usr/bin/env jython

from __future__ import absolute_import, division, print_function

from unittest import SkipTest, TestCase
from warnings import warn

try:
    from NativeImaging.backends.java import JavaImage
except ImportError as exc:
    warn('Unable to import Java imaging backend: %s' % exc)
    JavaImage = None

from .api import ApiConformanceTests


def setUpModule():
    import platform

    if platform.python_implementation() != 'Jython':
        raise SkipTest('JAI tests are only run on Jython')

    if not JavaImage:
        raise SkipTest('Java backend could not be imported: confirm that Java is installed')


class JavaImageTests(ApiConformanceTests, TestCase):
    IMAGE_CLASS = JavaImage

    def test_resize(self):
        # Ensure that we test standard behaviour:
        super(JavaImageTests, self).test_resize()

        img = self.open_sample_image()
        small = img.resize((128, 256))

        self.assertNotEqual(img._image, small._image)


if __name__ == "__main__":
    import unittest
    unittest.main()
