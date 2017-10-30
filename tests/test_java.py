#!/usr/bin/env jython

import unittest
import platform

if platform.python_implementation() != 'Jython':
    raise unittest.SkipTest('JAI tests are only run on Jython')

from NativeImaging.backends.java import JavaImage

from .api import ApiConformanceTests


class JavaImageTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = JavaImage

    def test_resize(self):
        # Ensure that we test standard behaviour:
        super(JavaImageTests, self).test_resize()

        img = self.open_sample_image()
        small = img.resize((128, 256))

        self.assertNotEqual(img._image, small._image)


if __name__ == "__main__":
    unittest.main()
