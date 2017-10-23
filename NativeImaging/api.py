from __future__ import absolute_import, division, print_function

# encoding: utf-8

"""
Our base "public" API, which is essentially the PIL Image class with almost
all methods raising :exc:`NotImplementedError`

Backends are implemented by subclassing and actually doing something with the
results
"""

# Constants defined to match PIL:

# transpose
FLIP_LEFT_RIGHT = 0
FLIP_TOP_BOTTOM = 1
ROTATE_90 = 2
ROTATE_180 = 3
ROTATE_270 = 4

# transforms
AFFINE = 0
EXTENT = 1
PERSPECTIVE = 2
QUAD = 3
MESH = 4

# resampling filters
NONE = 0
NEAREST = 0
ANTIALIAS = 1  # 3-lobed lanczos
LINEAR = BILINEAR = 2
CUBIC = BICUBIC = 3

# dithers
NONE = 0
NEAREST = 0
ORDERED = 1  # Not yet implemented
RASTERIZE = 2  # Not yet implemented
FLOYDSTEINBERG = 3  # default

# palettes/quantizers
WEB = 0
ADAPTIVE = 1

# categories
NORMAL = 0
SEQUENCE = 1
CONTAINER = 2


class Image(object):
    """
    Base class for all NativeImaging backends

    Should be compatible with PIL.Image or raise NotImplementedError()
    """

    format = None
    format_description = None
    im = None
    mode = ""
    size = (0, 0)
    palette = None
    info = {}
    readonly = 0

    def __init__(self):
        pass

    @classmethod
    def open(cls, fp, mode="r"):
        raise NotImplementedError()

    def __repr__(self):
        return "%(module)s.%(classname)s(%(id)s) <%(width)sx%(height)s, mode=%(mode)s>" % {
            'module': self.__class__.__module__,
            'classname': self.__class__.__name__,
            'mode': self.mode,
            'width': self.size[0],
            'height': self.size[1],
            'id': id(self)
        }

    def copy(self):
        """
        Returns an exact copy of the current image which may be destructively
        modified without affecting the original. Backends may choose to
        implement Copy-On-Write for performance so callers should not expect
        resource handles or object ids to change simply by calling copy().
        """
        raise NotImplementedError()

    def tostring(self, encoder_name="raw", *args):
        raise NotImplementedError()

    def tobitmap(self, name="image"):
        "Return image as an XBM bitmap"
        raise NotImplementedError()

    def fromstring(self, data, decoder_name="raw", *args):
        "Load data to image from binary string"
        raise NotImplementedError()

    def load(self):
        "Explicitly load pixel data."
        raise NotImplementedError()

    def verify(self):
        "Verify file contents."
        raise NotImplementedError()

    def convert(self, mode=None, data=None, dither=None,
                palette=WEB, colors=256):
        "Convert to other pixel format"
        raise NotImplementedError()

    def quantize(self, colors=256, method=0, kmeans=0, palette=None):
        raise NotImplementedError()

    def crop(self, box=None):
        """Return a cropped version of the image

        :param box: The crop rectangle, as a (left, upper, right, lower)-tuple.
        :rtype: :class:Image object
        """
        raise NotImplementedError()

    def draft(self, mode, size):
        """
        Configures the image file loader so it returns a version of the
        image that as closely as possible matches the given mode and
        size.  For example, you can use this method to convert a colour
        JPEG to greyscale while loading it, or to extract a 128x192
        version from a PCD file.
        """

        raise NotImplementedError()

    def filter(self, filter):
        """Apply environment filter to image

        Filters this image using the given filter. For a list of available
        filters, see the :mod:`ImageFilter` module.

        :param filter: Filter kernel.
        :rtype: :class:Image object
        """

        raise NotImplementedError()

    def getbands(self):
        """
        Returns a tuple containing the name of each band in this image.
        For example, getbands on an RGB image returns ("R", "G", "B").

        :return: A tuple containing band names.
        """
        raise NotImplementedError()

    def getbbox(self):
        """Get bounding box of actual data (non-zero pixels) in image

        Calculates the bounding box of the non-zero regions in the
        image.

        :return: The bounding box is returned as a 4-tuple defining the
           left, upper, right, and lower pixel coordinate. If the image
           is completely empty, this method returns None.
        """

        self.load()
        return self.im.getbbox()

    def getcolors(self, maxcolors=256):
        """Get colors from image, up to given limit
        Returns a list of colors used in this image.

        :param maxcolors: Maximum number of colors.  If this number is
           exceeded, this method returns None.  The default limit is
           256 colors.
        :return: An unsorted list of (count, pixel) values.
        """

        raise NotImplementedError()

    def getdata(self, band=None):
        """Get image data as sequence object"""
        raise NotImplementedError()

    def getextrema(self):
        """Get min/max value

        Gets the the minimum and maximum pixel values for each band in
        the image.

        :return: For a single-band image, a 2-tuple containing the
           minimum and maximum pixel value.  For a multi-band image,
           a tuple containing one 2-tuple for each band.
        """
        raise NotImplementedError()

    def getpalette(self):
        """Get palette contents

        :return: A list of color values [r, g, b, ...], or None if the
           image has no palette.
        """

        raise NotImplementedError()

    def getpixel(self, xy):
        """Get pixel value

        :param xy: The coordinate, given as (x, y).
        :return: The pixel value.  If the image is a multi-layer image,
           this method returns a tuple.
        """

        raise NotImplementedError()

    def getprojection(self):
        """Get projection to x and y axes

        Returns the horizontal and vertical projection.

        :return: Two sequences, indicating where there are non-zero
            pixels along the X-axis and the Y-axis, respectively.
        """

        raise NotImplementedError()

    def histogram(self, mask=None, extrema=None):
        """Take histogram of image

        Returns a histogram for the image. The histogram is returned as
        a list of pixel counts, one for each pixel value in the source
        image. If the image has more than one band, the histograms for
        all bands are concatenated (for example, the histogram for an
        "RGB" image contains 768 values).

        A bilevel image (mode "1") is treated as a greyscale ("L") image
        by this method.

        If a mask is provided, the method returns a histogram for those
        parts of the image where the mask image is non-zero. The mask
        image must have the same size as the image, and be either a
        bi-level image (mode "1") or a greyscale image ("L").

        :param mask: An optional mask.
        :return: A list containing pixel counts.
        """

        raise NotImplementedError()

    def paste(self, im, box=None, mask=None):
        """Paste other image into region

        Pastes another image into this image. The box argument is either
        a 2-tuple giving the upper left corner, a 4-tuple defining the
        left, upper, right, and lower pixel coordinate, or None (same as
        (0, 0)).  If a 4-tuple is given, the size of the pasted image
        must match the size of the region.

        If the modes don't match, the pasted image is converted to the
        mode of this image (see the :meth:`Image.convert` method for
        details).

        Instead of an image, the source can be a integer or tuple
        containing pixel values.  The method then fills the region
        with the given colour.  When creating RGB images, you can
        also use colour strings as supported by the ImageColor module.

        If a mask is given, this method updates only the regions
        indicated by the mask.  You can use either "1", "L" or "RGBA"
        images (in the latter case, the alpha band is used as mask).
        Where the mask is 255, the given image is copied as is.  Where
        the mask is 0, the current value is preserved.  Intermediate
        values can be used for transparency effects.

        Note that if you paste an "RGBA" image, the alpha band is
        ignored.  You can work around this by using the same image as
        both source image and mask.

        :param im: Source image or pixel value (integer or tuple).
        :param box: An optional 4-tuple giving the region to paste into.
           If a 2-tuple is used instead, it's treated as the upper left
           corner.  If omitted or None, the source is pasted into the
           upper left corner.

           If an image is given as the second argument and there is no
           third, the box defaults to (0, 0), and the second argument
           is interpreted as a mask image.
        :param mask: An optional mask image.
        :rtype: :class:Image object

        """

        raise NotImplementedError()

    def point(self, lut, mode=None):
        """Maps this image through a lookup table or function.

        :param lut: A lookup table, containing 256 values per band in the
           image. A function can be used instead, it should take a single
           argument. The function is called once for each possible pixel
           value, and the resulting table is applied to all bands of the
           image.
        :param mode: Output mode (default is same as input).  In the
           current version, this can only be used if the source image
           has mode "L" or "P", and the output has mode "1".
        :rtype: :class:Image object

        """

        raise NotImplementedError()

    def putalpha(self, alpha):
        """Set alpha layer
        Adds or replaces the alpha layer in this image.  If the image
        does not have an alpha layer, it's converted to "LA" or "RGBA".
        The new layer must be either "L" or "1".

        :param im: The new alpha layer.  This can either be an "L" or "1"
           image having the same size as this image, or an integer or
           other color value.

        """

        raise NotImplementedError()

    def putdata(self, data, scale=1.0, offset=0.0):
        """Put data from a sequence object into an image

        Copies pixel data to this image.  This method copies data from a
        sequence object into the image, starting at the upper left
        corner (0, 0), and continuing until either the image or the
        sequence ends.  The scale and offset values are used to adjust
        the sequence values: pixel = value*scale + offset.

        :param data: A sequence object.
        :param scale: An optional scale value.  The default is 1.0.
        :param offset: An optional offset value.  The default is 0.0.
        """

        raise NotImplementedError()

    def putpalette(self, data, rawmode="RGB"):
        "Put palette data into an image."
        raise NotImplementedError()

    def putpixel(self, xy, value):
        """
        Modifies the pixel at the given position. The colour is given as a
        single numerical value for single-band images, and a tuple for
        multi-band images.

        Note that this method is relatively slow. For more extensive changes,
        use :meth:`Image.paste` or the :mod:`ImageDraw` module instead.

        :param xy: The pixel coordinate, given as (x, y).
        :param value: The pixel value.
        """

        raise NotImplementedError()

    def resize(self, size, resample=NEAREST):
        """
        Returns a resized copy of this image.

        :param tuple size: The requested size in pixels, as a 2-tuple:
           (width, height).

        :param filter: An optional resampling filter.  This can be
           one of NEAREST (use nearest neighbour), BILINEAR
           (linear interpolation in a 2x2 environment), BICUBIC
           (cubic spline interpolation in a 4x4 environment), or
           ANTIALIAS (a high-quality downsampling filter).
        :rtype: :class:Image object
        """

        raise NotImplementedError()

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
        raise NotImplementedError()

    def save(self, fp, format=None, **params):
        """
        Saves this image under the given filename.  If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        Keyword options can be used to provide additional instructions
        to the writer. If a writer doesn't recognise an option, it is
        silently ignored. The available options are described later in
        this handbook.

        You can use a file object instead of a filename. In this case,
        you must always specify the format. The file object must
        implement the seek, tell, and write
        methods, and be opened in binary mode.

        :param file: File name or file object.
        :param format: Optional format override.  If omitted, the
           format to use is determined from the filename extension.
           If a file object was used instead of a filename, this
           parameter should always be used.
        :param params: Extra parameters to the image writer.
        :return: None
        :raises: :exc:`KeyError` If the output format could not be determined
                from the file name.  Use the format option to solve this.
        :raises: :exc:`IOError` If the file could not be written. The file may
                have been created, and may contain partial data.
        """

        raise NotImplementedError()

    def seek(self, frame):
        """
        Seeks to the given frame in this sequence file. If you seek beyond the
        end of the sequence, the method raises an EOFError exception. When a
        sequence file is opened, the library automatically seeks to frame 0.

        Note that in the current version of the library, most sequence formats
        only allows you to seek to the next frame.

        :param frame: Frame number, starting at 0.

        :exception: :exc:`EOFError` If the call attempts to seek beyond the
                    end of the sequence.

        See :meth:`Image.tell`
        """

        raise NotImplementedError()

    def show(self, title=None, command=None):
        """
        Displays this image. This method is mainly intended for debugging
        purposes.

        On Unix platforms, this method saves the image to a temporary PPM
        file, and calls the xv utility.

        On Windows, it saves the image to a temporary BMP file, and uses the
        standard BMP display utility to show it (usually Paint).

        :param title: Optional title to use for the image window,
           where possible.
        :type title: None or string
        """

        raise NotImplementedError()

    def split(self):
        """
        Split this image into individual bands. This method returns a tuple of
        individual image bands from an image. For example, splitting an "RGB"
        image creates three new images each containing a copy of one of the
        original bands (red, green, blue).

        :return: A tuple containing bands.
        """

        raise NotImplementedError()

    def tell(self):
        """Returns the current frame number.

        :return: Frame number, starting with 0.

        See :meth:`Image.seek`
        """

        raise NotImplementedError()

    def thumbnail(self, size, resample=NEAREST):
        """Create thumbnail representation (modifies image in place)

        Make this image into a thumbnail. This method modifies the image to
        contain a thumbnail version of itself, no larger than the given size.
        This method calculates an appropriate thumbnail size to preserve the
        aspect of the image, calls the :meth:`Image.draft` method to
        configure the file reader (where applicable), and finally resizes the
        image.

        Also note that this function modifies the Image object in place. If
        you need to use the full resolution image as well, apply this method
        to a :meth:`Image.copy` of the original image.

        :param size: Requested size.
        :param resample: Optional resampling filter. This can be one of of
            NEAREST, BILINEAR, BICUBIC, or ANTIALIAS (best quality). If omitted,
            it defaults to NEAREST (this will be changed to ANTIALIAS in a future
            version).
        :rtype: None
        """

        raise NotImplementedError()

    def transform(self, size, method, data=None, resample=NEAREST, fill=1):
        """
        Transforms this image. This method creates a new image with the given
        size, and the same mode as the original, and copies data to the new
        image using the given transform.

        :param size: The output size.
        :param method: The transformation method.  This is one of
          EXTENT (cut out a rectangular subregion), AFFINE
          (affine transform), PERSPECTIVE (perspective
          transform), QUAD (map a quadrilateral to a
          rectangle), or MESH (map a number of source quadrilaterals
          in one operation).
        :param data: Extra data to the transformation method.
        :param resample: Optional resampling filter.  It can be one of
           NEAREST (use nearest neighbour), BILINEAR
           (linear interpolation in a 2x2 environment), or
           BICUBIC (cubic spline interpolation in a 4x4
           environment). If omitted, or if the image has mode
           "1" or "P", it is set to NEAREST.
        :rtype: :class:Image object
        """

        raise NotImplementedError()

    def transpose(self, method):
        "Transpose image (flip or rotate in 90 degree steps)"

        raise NotImplementedError()
