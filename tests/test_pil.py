from __future__ import absolute_import, division, print_function

import unittest

from .api import ApiConformanceTests
from NativeImaging import get_image_class


class PILTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = get_image_class("PIL")


if __name__ == "__main__":
    unittest.main()
