"""
An Image-compatible backend using Aware via ctypes
"""

import ctypes
from ctypes.util import find_library

from NativeImaging.api import Image
from PIL import Image as PILImage

_path = find_library("awj2k")

if not _path:
    raise ImportError("Unable to find aware library!")

_lib = ctypes.CDLL(_path)


def _aware_errcheck(rc, func, args):
    if rc:
        raise AwareException("Error: '%s' returned '%d'" % (func.__name__, rc))
    else:
        return rc


class AwareException(Exception):
    pass


class J2KObject(ctypes.Structure):
    pass


J2K_OBJECT_P = ctypes.POINTER(J2KObject)

AW_J2K_PRESERVE_ASPECT_RATIO = -1
AW_J2K_PRESERVE_ASPECT_RATIO_NO_PAD = -2
AW_J2K_MODIFY_ASPECT_RATIO = -3


aw_j2k_create = _lib.aw_j2k_create
aw_j2k_create.restype = ctypes.c_uint
aw_j2k_create.argtypes = [ctypes.c_void_p]
aw_j2k_create.errcheck = _aware_errcheck

aw_j2k_destroy = _lib.aw_j2k_destroy
aw_j2k_destroy.restype = ctypes.c_uint
aw_j2k_destroy.argtypes = [ctypes.c_void_p]

aw_j2k_set_input_image = _lib.aw_j2k_set_input_image
aw_j2k_set_input_image.restype = ctypes.c_uint
aw_j2k_set_input_image.argtypes = [ctypes.c_void_p,
                                   ctypes.c_void_p, ctypes.c_size_t]
aw_j2k_set_input_image.errcheck = _aware_errcheck

aw_j2k_get_input_image_info = _lib.aw_j2k_get_input_image_info
aw_j2k_get_input_image_info.restype = ctypes.c_uint
aw_j2k_get_input_image_info.argtypes = [ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong)]
aw_j2k_set_input_image.errcheck = _aware_errcheck

aw_j2k_set_input_j2k_region_level = _lib.aw_j2k_set_input_j2k_region_level
aw_j2k_set_input_j2k_region_level.restype = ctypes.c_uint
aw_j2k_set_input_j2k_region_level.argtypes = [ctypes.c_void_p,
                                              ctypes.c_int, ctypes.c_int,
                                              ctypes.c_int, ctypes.c_int]
aw_j2k_set_input_j2k_region_level.errcheck = _aware_errcheck


aw_j2k_set_output_com_image_size = _lib.aw_j2k_set_output_com_image_size
aw_j2k_set_output_com_image_size.restype = ctypes.c_uint
aw_j2k_set_output_com_image_size.argtypes = [ctypes.c_void_p,
                                             ctypes.c_int, ctypes.c_int,
                                             ctypes.c_int]
aw_j2k_set_output_com_image_size.errcheck = _aware_errcheck


aw_j2k_get_output_image_raw = _lib.aw_j2k_get_output_image_raw
aw_j2k_get_output_image_raw.restype = ctypes.c_uint
aw_j2k_get_output_image_raw.argtypes = [ctypes.c_void_p,
                                        ctypes.POINTER(ctypes.POINTER(ctypes.c_char)),
                                        ctypes.POINTER(ctypes.c_size_t),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.POINTER(ctypes.c_ulong),
                                        ctypes.c_int]
aw_j2k_get_output_image_raw.errcheck = _aware_errcheck

aw_j2k_free = _lib.aw_j2k_free
aw_j2k_free.restype = ctypes.c_uint
aw_j2k_free.argtypes = [ctypes.c_void_p,
                        ctypes.POINTER(ctypes.c_char)]
aw_j2k_free.errcheck = _aware_errcheck

aw_j2k_set_input_j2k_resolution_level = _lib.aw_j2k_set_input_j2k_resolution_level
aw_j2k_set_input_j2k_resolution_level.restype = ctypes.c_uint
aw_j2k_set_input_j2k_resolution_level.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_int,
                                                  ctypes.c_int]
aw_j2k_set_input_j2k_resolution_level.errcheck = _aware_errcheck


MAX_PROGRESSION_LEVEL = 6
FULL_XFORM_FLAG = 0


def scaled_dimension(progression_level, dimension):
    scale_factor = 2 << (progression_level - 1)
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
        self._j2k_object_p = ctypes.c_void_p()
        aw_j2k_create(ctypes.byref(self._j2k_object_p))
        assert self._j2k_object_p.value, "failed to create j2k_object"

    def __del__(self):
        if self._j2k_object_p:
            if aw_j2k_destroy:
                aw_j2k_destroy(self._j2k_object_p)

    @classmethod
    def open(cls, fp, mode="rb"):
        i = cls()

        if isinstance(fp, basestring):
            fp = open(fp, "rb")

        b = ctypes.create_string_buffer(fp.read())
        aw_j2k_set_input_image(i._j2k_object_p, b, ctypes.sizeof(b))

        return i

    @property
    def size(self):
        rows = ctypes.c_ulong()
        cols = ctypes.c_ulong()
        bpp = ctypes.c_ulong()
        nChannels = ctypes.c_ulong()
        aw_j2k_get_input_image_info(self._j2k_object_p,
                                    ctypes.byref(cols),
                                    ctypes.byref(rows),
                                    ctypes.byref(bpp),
                                    ctypes.byref(nChannels))
        return (cols.value, rows.value)

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
        aw_j2k_set_output_com_image_size(self._j2k_object_p, height, width,
                                         AW_J2K_PRESERVE_ASPECT_RATIO_NO_PAD)
        # TODO: remove preserve aspect ratio out into chronam code.
        return self.copy()

    def crop(self, box):
        x1, y1, x2, y2 = box
        self.__crop = box
        aw_j2k_set_input_j2k_region_level(self._j2k_object_p, x1, y1, x2, y2)
        return self

    def copy(self):
        if self.__crop:
            x1, y1, x2, y2 = self.__crop
            width, height = self.__resize
            level = desired_progression_level(x1, x2, y1, y2, width, height)
            aw_j2k_set_input_j2k_resolution_level(self._j2k_object_p,
                                                  level,
                                                  FULL_XFORM_FLAG)

        data_p = ctypes.pointer(ctypes.POINTER(ctypes.c_char)())
        data_length = ctypes.c_size_t()
        rows = ctypes.c_ulong()
        cols = ctypes.c_ulong()
        nChannels = ctypes.c_ulong()
        bpp = ctypes.c_ulong()

        aw_j2k_get_output_image_raw(self._j2k_object_p,
                                    data_p,
                                    ctypes.byref(data_length),
                                    ctypes.byref(rows),
                                    ctypes.byref(cols),
                                    ctypes.byref(nChannels),
                                    ctypes.byref(bpp), 0)
        data = data_p.contents[0:data_length.value]

        image = PILImage.frombuffer("L", (cols.value, rows.value),
                                    data,
                                    "raw", "L", 0, 1)
        aw_j2k_free(self._j2k_object_p, data_p.contents)
        return image

    def save(self, fp, format="JPEG", **kwargs):
        return self.copy().save(fp, format, **kwargs)
