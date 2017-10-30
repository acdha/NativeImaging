from __future__ import absolute_import, division, print_function

import unittest

from NativeImaging import get_image_class

from .api import ApiConformanceTests

try:
    AWARE_IMAGE_CLASS = get_image_class("aware")
except ImportError:
    AWARE_IMAGE_CLASS = None


@unittest.skipUnless(AWARE_IMAGE_CLASS, 'Aware ctypes backend is not not available')
class AwareTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = AWARE_IMAGE_CLASS


if __name__ == "__main__":
    unittest.main()
