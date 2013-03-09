"""
An Image-compatible backend using Aware via an extension module.
"""

from PIL import Image as PILImage
from NativeImaging.api import Image

import _aware


AW_J2K_PRESERVE_ASPECT_RATIO = -1
AW_J2K_PRESERVE_ASPECT_RATIO_NO_PAD = -2
AW_J2K_MODIFY_ASPECT_RATIO = -3

MAX_PROGRESSION_LEVEL = 6


def scaled_dimension(progression_level, dimension):
    scale_factor = 2<<(progression_level-1)
    return dimension / float(scale_factor)


def desired_progression_level(x1, x2, y1, y2, width, height):
    level = MAX_PROGRESSION_LEVEL
    while level > 1 and \
            width > scaled_dimension(level, x2 - x1) and \
            height > scaled_dimension(level, y2 - y1):
        level -= 1
    return level


class AwareImage(Image):

    NONE = NEAREST = 0
    ANTIALIAS = 1

    def __init__(self):
        self.__crop = None
        self.__resize = None
        self._j2k_object_p = _aware.j2k_create()
        assert self._j2k_object_p, "failed to create j2k_object"

    def __del__(self):
        if self._j2k_object_p:
            _aware.j2k_destroy(self._j2k_object_p)

    @classmethod
    def open(cls, fp, mode="rb"):
        i = cls()
        if isinstance(fp, basestring):
            fp = open(fp, "rb")
        _aware.j2k_set_input_image(i._j2k_object_p, fp.read())
        return i

    @property
    def size(self):
        cols, rows, bpp, channels = _aware.j2k_get_input_image_info(
            self._j2k_object_p)
        return cols, rows

    def thumbnail(self, size, resample=ANTIALIAS):
        x, y = self.size

        if x > size[0]:
            y = max(y * size[0] / x, 1)
            x = size[0]
        if y > size[1]:
            x = max(x * size[1] / y, 1)
            y = size[1]

        new_size = (x, y)
        return self.resize(new_size, resample=resample)

    def resize(self, size, resample=ANTIALIAS):
        width, height = int(size[0]), int(size[1])
        self.__resize = (width, height)
        return self.copy()

    def crop(self, box):
        x1, y1, x2, y2 = box
        self.__crop = box
        return self

    def copy(self):
        if self.__crop:
            x1, y1, x2, y2 = self.__crop
            width, height = self.__resize
            level = desired_progression_level(x1, x2, y1, y2, width, height)
            _aware.j2k_set_input_j2k_resolution_level(self._j2k_object_p,
                                                      level)
            _aware.j2k_set_input_j2k_region_level(self._j2k_object_p,
            x1, y1, x2, y2)

        if self.__resize:
            width, height = self.__resize
            try:
                _aware.j2k_set_output_com_image_size(self._j2k_object_p,
                                                     height, width,
                                                     AW_J2K_MODIFY_ASPECT_RATIO)
            except _aware.error, e:
                pass

        result = _aware.j2k_get_output_image_raw(self._j2k_object_p)
        rows, cols, nChannels, bpp, data = result
        image = PILImage.frombuffer("L", (cols, rows), data, "raw", "L", 0, 1)
        if self.__resize and image.size!=self.__resize:
            image.resize((width, height))
        return image

    def save(self, fp, format="JPEG", **kwargs):
        return self.copy().save(fp, format, **kwargs)


if __name__=="__main__":
    from NativeImaging.backends.aware_cext import AwareImage as Image

    from urllib2 import urlopen
    JP2_URL = 'http://chroniclingamerica.loc.gov/data/hihouml/batch_hihouml_cardinal_ver01/data/sn83025121/00211108897/1882020101/0015.jp2'
    fp = urlopen(JP2_URL)

    i = Image.open(fp)
    print "size:", i.size
    im = i.crop((1000, 1000, 2000, 3000))
    im = im.resize((200, 300))
    print "resized to:", im.size
    im.save(open("/tmp/foo.jpeg", "wb"), format="JPEG")

    im = i.crop((100, 100, 200, 300))
    im = im.resize((200, 300))
    print "resized to:", im.size
