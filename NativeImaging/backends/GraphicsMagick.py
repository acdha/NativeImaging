# encoding: utf-8
"""
An Image-compatible backend using GraphicsMagick via ctypes
"""

import ctypes

from NativeImaging.api import Image

import wand_wrapper as wand

class GraphicsMagickImage(Image):
    _wand = None

    NONE = NEAREST = 0
    ANTIALIAS = wand.FilterTypes['LanczosFilter']
    CUBIC = BICUBIC = wand.FilterTypes['CubicFilter']

    def __init__(self):
        self._wand = wand.NewMagickWand()
        assert self._wand, "NewMagickWand() failed???"

    def __del__(self):
        if self._wand:
            self._wand = wand.DestroyMagickWand(self._wand)

    @classmethod
    def open(cls, fp, mode="rb"):
        i = cls()

        if isinstance(fp, basestring):
            wand.MagickReadImage(i._wand, fp)
        elif isinstance(fp, file):
            c_file = ctypes.pythonapi.PyFile_AsFile(fp)
            wand.MagickReadImageFile(i._wand, c_file)
        elif hasattr(fp, "read"):
            b = ctypes.create_string_buffer(fp.read())
            wand.MagickReadImageBlob(i._wand, b, ctypes.sizeof(b))
        else:
            raise ValueError("Cannot open %r object" % fp)

        return i

    @property
    def size(self):
        width = wand.MagickGetImageWidth(self._wand)
        height = wand.MagickGetImageHeight(self._wand)
        return (width, height)

    def thumbnail(self, size, resample=ANTIALIAS):
        x, y = self.size

        if x > size[0]: y = max(y * size[0] / x, 1); x = size[0]
        if y > size[1]: x = max(x * size[1] / y, 1); y = size[1]

        new_size = (x, y)

        wand.MagickStripImage(self._wand)
        return self.resize(new_size, resample=resample)

    def resize(self, size, resample=ANTIALIAS):
        width, height = int(size[0]), int(size[1])
        wand.MagickResizeImage(self._wand, width, height, resample, 1)
        return self  # TODO: return copy

    def crop(self, box):
        x0, y0, x1, y1 = box
        width = x1 - x0;
        height = y1 - y1;
        wand.MagickCropImage(self._wand, x0, y0, width, height)
        return self  # TODO: return copy?

    def save(self,  fp, format="JPEG", **kwargs):
        wand.MagickSetImageFormat(self._wand, format)
        assert format == wand.MagickGetImageFormat(self._wand)

        if isinstance(fp, basestring):
            wand.MagickWriteImage(self._wand, fp)
        elif isinstance(fp, file):
            c_file = ctypes.pythonapi.PyFile_AsFile(fp)
            wand.MagickReadImageFile(self._wand, c_file)
        elif hasattr(fp, "write"):
            length = ctypes.c_size_t()
            data = wand.MagickWriteImageBlob(self._wand, ctypes.pointer(length))
            fp.write(data[0:length.value])
        else:
            raise ValueError("Don't know how to write to a %r" % fp)
