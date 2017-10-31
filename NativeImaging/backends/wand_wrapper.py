# encoding: utf-8
"""
ctypes wrappers for GraphicsMagick functions with error-handling

n.b. Heavy consultation of http://www.graphicsmagick.org/wand/magick_wand.html
and the ctypes documentation is advised
"""

import ctypes
import sys
from ctypes.util import find_library

_wandlib_path = find_library("GraphicsMagickWand")

if not _wandlib_path:
    raise ImportError("Unable to find GraphicsMagicWand library!")

_wandlib = ctypes.CDLL(_wandlib_path)
_wandlib.InitializeMagick(sys.argv[0])

libc = ctypes.CDLL(find_library("libc"))


def _wand_errcheck(rc, func, args):
    """
    Intended for use as a ctypes errcheck function

    Can only be used with functions which take Wand as their first argument
    """

    if not rc:
        err_type = ExceptionType()
        description = MagickGetException(args[0], err_type)

        if err_type.value == 430:  # "Unable to open file"
            raise IOError(description)
        else:
            raise WandException(description)
    else:
        return rc


# ENUM declarations:
FilterTypes = {
    'UndefinedFilter': 0,
    'PointFilter': 1,
    'BoxFilter': 2,
    'TriangleFilter': 3,
    'HermiteFilter': 4,
    'HanningFilter': 5,
    'HammingFilter': 6,
    'BlackmanFilter': 7,
    'GaussianFilter': 8,
    'QuadraticFilter': 9,
    'CubicFilter': 10,
    'CatromFilter': 11,
    'MitchellFilter': 12,
    'LanczosFilter': 13,
    'BesselFilter': 14,
    'SincFilter': 15,
}


class WandException(Exception):
    pass


class MagickWand(ctypes.Structure):
    pass


WAND_P = ctypes.POINTER(MagickWand)


class FILE(ctypes.Structure):
    pass


ExceptionType = ctypes.c_int  # TODO: Expand enum choices
MagickBooleanType = ctypes.c_uint

FILE_P = ctypes.POINTER(FILE)

# C definition:
# FILE *fdopen(int fd, const char *mode);
fdopen = libc.fdopen
fdopen.argtypes = (ctypes.c_int, ctypes.c_char_p)
fdopen.restype = FILE_P


def c_file_from_py_file(py_file, flags):
    return fdopen(py_file.fileno(), flags)


MagickGetException = _wandlib.MagickGetException
MagickGetException.restype = ctypes.c_char_p
MagickGetException.argtypes = [WAND_P, ctypes.POINTER(ExceptionType)]

NewMagickWand = _wandlib.NewMagickWand
NewMagickWand.restype = WAND_P
NewMagickWand.errcheck = _wand_errcheck

CloneMagickWand = _wandlib.CloneMagickWand
CloneMagickWand.restype = WAND_P
CloneMagickWand.argtypes = [WAND_P]
CloneMagickWand.errcheck = _wand_errcheck

DestroyMagickWand = _wandlib.DestroyMagickWand
DestroyMagickWand.argtypes = [WAND_P]
DestroyMagickWand.restype = MagickBooleanType
DestroyMagickWand.errcheck = _wand_errcheck

MagickStripImage = _wandlib.MagickStripImage
MagickStripImage.argtypes = [WAND_P]
MagickStripImage.restype = MagickBooleanType
MagickStripImage.errcheck = _wand_errcheck

# The file I/O functions are complicated by the need to convert Python file-like
# objects into something compatible with ctypes or CFFI:
_MagickReadImageBlob = _wandlib.MagickReadImageBlob
_MagickReadImageBlob.restype = MagickBooleanType
_MagickReadImageBlob.argtypes = [WAND_P, ctypes.c_void_p, ctypes.c_size_t]
_MagickReadImageBlob.errcheck = _wand_errcheck


def MagickReadImageBlob(wand, blob):
    b = ctypes.create_string_buffer(blob)
    return _MagickReadImageBlob(wand, b, ctypes.sizeof(b))


_MagickReadImageFile = _wandlib.MagickReadImageFile
_MagickReadImageFile.restype = MagickBooleanType
_MagickReadImageFile.argtypes = [WAND_P, FILE_P]
_MagickReadImageFile.errcheck = _wand_errcheck


def MagickReadImageFile(wand, fp):
    return _MagickReadImageFile(wand, c_file_from_py_file(fp, b'rb'))


MagickWriteImage = _wandlib.MagickWriteImage
MagickWriteImage.restype = MagickBooleanType
MagickWriteImage.argtypes = [WAND_P, ctypes.c_char_p]
MagickWriteImage.errcheck = _wand_errcheck

_MagickWriteImageBlob = _wandlib.MagickWriteImageBlob
_MagickWriteImageBlob.restype = ctypes.POINTER(ctypes.c_char)
_MagickWriteImageBlob.argtypes = [WAND_P, ctypes.POINTER(ctypes.c_size_t)]
_MagickWriteImageBlob.errcheck = _wand_errcheck


def MagickWriteImageBlob(wand):
    length = ctypes.c_size_t()
    data = _MagickWriteImageBlob(wand, ctypes.pointer(length))
    return data[0:length.value]


_MagickWriteImageFile = _wandlib.MagickWriteImageFile
_MagickWriteImageFile.restype = MagickBooleanType
_MagickWriteImageFile.argtypes = [WAND_P, FILE_P]
_MagickWriteImageFile.errcheck = _wand_errcheck


def MagickWriteImageFile(wand, fp):
    _MagickWriteImageFile(wand, c_file_from_py_file(fp, b'wb'))


MagickReadImage = _wandlib.MagickReadImage
MagickReadImage.restype = MagickBooleanType
MagickReadImage.argtypes = [WAND_P, ctypes.c_char_p]
MagickReadImage.errcheck = _wand_errcheck

MagickGetImageHeight = _wandlib.MagickGetImageHeight
MagickGetImageHeight.restype = ctypes.c_ulong
MagickGetImageHeight.argtypes = (WAND_P, )
MagickGetImageHeight.errcheck = _wand_errcheck

MagickGetImageWidth = _wandlib.MagickGetImageWidth
MagickGetImageWidth.restype = ctypes.c_ulong
MagickGetImageWidth.argtypes = (WAND_P, )
MagickGetImageWidth.errcheck = _wand_errcheck

MagickGetImageFormat = _wandlib.MagickGetImageFormat
MagickGetImageFormat.restype = ctypes.c_char_p
MagickGetImageFormat.argtypes = (WAND_P, )
MagickGetImageFormat.errcheck = _wand_errcheck

MagickSetImageFormat = _wandlib.MagickSetImageFormat
MagickSetImageFormat.restype = MagickBooleanType
MagickSetImageFormat.argtypes = [WAND_P, ctypes.c_char_p]
MagickSetImageFormat.errcheck = _wand_errcheck

MagickSetCompressionQuality = _wandlib.MagickSetCompressionQuality
MagickSetCompressionQuality.restype = MagickBooleanType
MagickSetCompressionQuality.argtypes = [WAND_P, ctypes.c_ulong]
MagickSetCompressionQuality.errcheck = _wand_errcheck

MagickScaleImage = _wandlib.MagickScaleImage
MagickScaleImage.restype = MagickBooleanType
MagickScaleImage.argtypes = [WAND_P, ctypes.c_ulong, ctypes.c_ulong]
MagickScaleImage.errcheck = _wand_errcheck

MagickResizeImage = _wandlib.MagickScaleImage
MagickResizeImage.restype = MagickBooleanType
MagickResizeImage.argtypes = [WAND_P, ctypes.c_ulong, ctypes.c_ulong]
MagickResizeImage.errcheck = _wand_errcheck

MagickCropImage = _wandlib.MagickCropImage
MagickCropImage.restype = MagickBooleanType
MagickCropImage.argtypes = [WAND_P, ctypes.c_ulong, ctypes.c_ulong,
                            ctypes.c_ulong, ctypes.c_ulong]
MagickCropImage.errcheck = _wand_errcheck
