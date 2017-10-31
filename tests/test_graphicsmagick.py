from __future__ import absolute_import, division, print_function

import unittest

from NativeImaging.backends.GraphicsMagick import GraphicsMagickImage

from .api import ApiConformanceTests


class GraphicsMagickTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = GraphicsMagickImage

    # These stubs exist to avoid expectedFailure setting
    # __unittest_expecting_failure__ on the superclass method and
    # thus causing unexpected successes for every other subclass

    @unittest.expectedFailure
    def test_rotate_arb(*args, **kwargs):
        return super().test_rotate_arb(*args, **kwargs)

    @unittest.expectedFailure
    def test_rotate_90(*args, **kwargs):
        return super().test_rotate_90(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
