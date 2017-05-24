from __future__ import absolute_import, division, print_function

import unittest

from .api import ApiConformanceTests
from NativeImaging.backends.GraphicsMagick import GraphicsMagickImage


class GraphicsMagickTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = GraphicsMagickImage

    test_rotate_arb = unittest.expectedFailure(ApiConformanceTests.test_rotate_arb)
    test_rotate_90 = unittest.expectedFailure(ApiConformanceTests.test_rotate_90)


if __name__ == "__main__":
    unittest.main()
