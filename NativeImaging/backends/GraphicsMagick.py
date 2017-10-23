# encoding: utf-8
"""
An Image-compatible backend using GraphicsMagick
"""

from copy import deepcopy
import sys

from NativeImaging.api import Image

try:
    from . import wand_wrapper_cffi as wand
except ImportError:
    from . import wand_wrapper as wand

if sys.version_info >= (3, ):
    basestring = str
else:
    pass


class GraphicsMagickImage(Image):
    _wand = None

    NONE = NEAREST = 0
    ANTIALIAS = wand.FilterTypes['LanczosFilter']
    CUBIC = BICUBIC = wand.FilterTypes['CubicFilter']

    def __init__(self, magick_wand=None):
        if magick_wand is None:
            self._wand = wand.NewMagickWand()
        else:
            self._wand = magick_wand
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
            wand.MagickReadImageFile(i._wand, fp)
        elif hasattr(fp, "read"):
            wand.MagickReadImageBlob(i._wand, fp.read())
        else:
            raise IOError("Cannot open %r object" % fp)

        return i

    def copy(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        # We have a little bit of song-and-dance here because we need to avoid
        # deepcopy() attempting to copy _wand, which would be pointless since
        # we're about to replace it anyway:
        new_wand = wand.CloneMagickWand(self._wand)
        new_image = GraphicsMagickImage(magick_wand=new_wand)

        for k in self.__dict__:
            if k == "_wand":
                continue
            setattr(new_image, k, deepcopy(getattr(self, k), memo))

        return new_image

    @property
    def size(self):
        width = wand.MagickGetImageWidth(self._wand)
        height = wand.MagickGetImageHeight(self._wand)
        return (width, height)

    def thumbnail(self, size, resample=ANTIALIAS):
        width, height = self.size

        if width > size[0]:
            height = max(height * size[0] / width, 1)
            width = size[0]

        if height > size[1]:
            width = max(width * size[1] / height, 1)
            height = size[1]

        wand.MagickStripImage(self._wand)
        wand.MagickResizeImage(self._wand, width, height, resample, 1)

    def resize(self, size, resample=ANTIALIAS):
        width, height = int(size[0]), int(size[1])

        im = self.copy()

        wand.MagickResizeImage(im._wand, width, height, resample, 1)

        return im

    def crop(self, box):
        # TODO: Investigate whether this can be further optimized by using the
        # lower-level GraphicsMagick CropImage function directly since that is
        # non-destructive:
        # http://www.graphicsmagick.org/api/transform.html#cropimage
        x0, y0, x1, y1 = box
        width = x1 - x0
        height = y1 - y0

        im = self.copy()

        wand.MagickCropImage(im._wand, width, height, x0, y0)

        return im

    def save(self, fp, format="JPEG", **kwargs):
        if 'quality' in kwargs:
            wand.MagickSetCompressionQuality(self._wand, kwargs['quality'])

        wand.MagickSetImageFormat(self._wand, format)
        assert format == wand.MagickGetImageFormat(self._wand)

        if isinstance(fp, basestring):
            wand.MagickWriteImage(self._wand, fp)
        elif isinstance(fp, file):
            wand.MagickWriteImageFile(self._wand, fp)
        elif hasattr(fp, "write"):
            data = wand.MagickWriteImageBlob(self._wand)
            fp.write(data)
        else:
            raise ValueError("Don't know how to write to a %r" % fp)
