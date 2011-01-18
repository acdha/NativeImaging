import unittest

from api import ApiConformanceTests

from NativeImaging.backends.GraphicsMagick import GraphicsMagickImage

class GraphicsMagickTests(ApiConformanceTests, unittest.TestCase):
    IMAGE_CLASS = GraphicsMagickImage

if __name__ == "__main__":
    unittest.main()

