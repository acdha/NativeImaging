# encoding: utf-8
"""
An Image-compatible backend for Jython which uses the native Java Advanced
Imaging framework

Why not use Java Image I/O? Because it's buggy and tends to choke on EXIF
data, different colorspaces, etc. Representative post:
http://stackoverflow.com/questions/4470958/why-does-loading-this-jpg-using-javaio-give-cmmexception
"""

from __future__ import absolute_import, division

import math
import sys
from array import array
from copy import deepcopy

from com.sun.media.jai.codec import ByteArraySeekableStream
from java.awt.image.renderable import ParameterBlock
from java.io import ByteArrayOutputStream
from java.lang import Float
from javax.media.jai import JAI, Interpolation
from javax.media.jai.operator import TransposeDescriptor
from NativeImaging.api import Image


class JavaImage(Image):
    NONE = NEAREST = Interpolation.INTERP_NEAREST
    ANTIALIAS = Interpolation.INTERP_BILINEAR
    CUBIC = BICUBIC = Interpolation.INTERP_BICUBIC

    @classmethod
    def open(cls, fp, mode="rb"):
        i = cls()

        if isinstance(fp, basestring):
            try:
                i._image = JAI.create("fileload", fp)
            except:
                # JAI uses "IllegalArgumentException" for problems like "File
                # does not exist" and we'd like to return a more appropriate
                # exception where possible:

                e = sys.exc_info()[1]

                raise IOError("Unable to open %s: %s" % (fp, e))

        elif not hasattr(fp, "read"):
            raise TypeError("Don't know how to open a %r" % fp)

        else:

            try:
                byte_array = array("b")
                # array.fromfile() is documented as not supporting file-like
                # objects and we'd like to support both:
                byte_array.fromstring(fp.read())

                bs = ByteArraySeekableStream(byte_array)

                i._image = JAI.create("stream", bs)
            except:
                # See above
                e = sys.exc_info()[1]
                raise IOError("Unable to open %r: %s" % (fp, e))

        return i

    def copy(self):
        return deepcopy(self)

    @property
    def size(self):
        width = self._image.getWidth()
        height = self._image.getHeight()
        return (width, height)

    def thumbnail(self, size, resample=ANTIALIAS):
        width, height = self.size

        if width > size[0]:
            height = max(height * size[0] / width, 1)
            width = size[0]

        if height > size[1]:
            width = max(width * size[1] / height, 1)
            height = size[1]

        self._image = self._resize((width, height), resample)

    def resize(self, size, resample=ANTIALIAS):
        im = self.copy()
        im._image = self._resize(size, resample)
        return im

    def _resize(self, size, resample=ANTIALIAS):
        width, height = int(size[0]), int(size[1])

        pb = ParameterBlock()
        pb.addSource(self._image)
        # Since the scale & translate factors are passed using a generic-type
        # method we have to explicitly wrap them in java.lang.Float as the
        # default auto-bridged Double is not supported:
        pb.add(Float(width / self._image.getWidth()))    # x scale factor
        pb.add(Float(height / self._image.getHeight()))  # y scale factor
        pb.add(Float(0.0))                               # x translation
        pb.add(Float(0.0))                               # y translation
        pb.add(Interpolation.getInstance(resample))

        # Possible quality tweaks we might want to expose:
        # RenderingHints qualityHints = new RenderingHints(RenderingHints.KEY_RENDERING,
        #     RenderingHints.VALUE_RENDER_QUALITY)
        #
        # RenderedOp resizedImage = JAI.create("SubsampleAverage",
        #     image, scale, scale, qualityHints)

        return JAI.create("scale", pb)

    def crop(self, box):
        x0, y0, x1, y1 = box
        width = x1 - x0
        height = y1 - y0

        im = self.copy()

        pb = ParameterBlock()
        pb.addSource(self._image)
        pb.add(Float(x0))
        pb.add(Float(y0))
        pb.add(Float(width))
        pb.add(Float(height))

        im._image = JAI.create("crop", pb)

        return im

    def rotate(self, angle, filter=NEAREST, expand=False):
        """
        Returns a rotated copy of this image.  This method returns a
        copy of this image, rotated the given number of degrees counter
        clockwise around its centre.

        :param angle: In degrees counter clockwise.
        :param filter: An optional resampling filter.  This can be
           one of NEAREST (use nearest neighbour), BILINEAR
           (linear interpolation in a 2x2 environment), or BICUBIC
           (cubic spline interpolation in a 4x4 environment).
           If omitted, or if the image has mode "1" or "P", it is
           set NEAREST.
        :param expand: Optional expansion flag.  If true, expands the output
           image to make it large enough to hold the entire rotated image.
           If false or omitted, make the output image the same size as the
           input image.
        :rtype: :class:Image object
        """

        radians = angle * (math.pi / 180.0)

        im = self.copy()

        pb = ParameterBlock()
        pb.addSource(self._image)

        transpose = None

        # In many cases we can simply transpose the image:
        if angle == 90:
            transpose = TransposeDescriptor.ROTATE_90
        elif angle == 180:
            transpose = TransposeDescriptor.ROTATE_180
        elif angle == 270:
            transpose = TransposeDescriptor.ROTATE_270

        if transpose:
            pb.add(transpose)
            im._image = JAI.create("transpose", pb)
            return im

        # looks like we have to do this the slow way:
        pb.add(Float(0.0))
        pb.add(Float(0.0))
        pb.add(Float(radians))
        pb.add(Interpolation.getInstance(filter))

        im._image = JAI.create("rotate", pb)

        # Rotate can leave the origin negative; we'll bump it back so our
        # future operations don't need to worry about this:
        if im._image.minX < 0 or im._image.minY < 0:
            pb = ParameterBlock()
            pb.addSource(im._image)
            pb.add(Float(im._image.minX * -1))
            pb.add(Float(im._image.minY * -1))
            im._image = JAI.create("translate", pb)

        if not expand:
            pb = ParameterBlock()
            pb.addSource(im._image)
            pb.add(Float(0))
            pb.add(Float(0))
            pb.add(Float(self._image.getWidth()))
            pb.add(Float(self._image.getHeight()))

            im._image = JAI.create("crop", pb)

        return im

    def save(self, fp, format="JPEG", **kwargs):
        if isinstance(fp, basestring):
            fp = open(fp, mode="wb")
        elif not hasattr(fp, "write"):
            raise ValueError("Don't know how to write to a %r" % fp)

        bos = ByteArrayOutputStream()

        JAI.create("encode", self._image, bos, format.lower())

        fp.write(bos.toByteArray())
        fp.flush()
