# encoding: utf-8
"""
cffi wrappers for GraphicsMagick functions with error-handling

n.b. Heavy consultation of http://www.graphicsmagick.org/wand/magick_wand.html
and the cffi documentation is advised
"""

from functools import wraps
import sys

from cffi import FFI

ffi = FFI()


class WandException(Exception):
    pass


def check_rc(f):
    @wraps(f)
    def inner(*args):
        rc = f(*args)
        if not rc:
            err_type = ffi.new("ExceptionType *")

            desc_cdata = _wand.MagickGetException(args[0], err_type)
            description = ffi.string(desc_cdata)

            if err_type[0] == 430:  # "Unable to open file"
                raise IOError(description)
            else:
                raise WandException(description)
        else:
            return rc
    return inner

def returns_string(f):
    """Decorator which ensures that char* objects return simply Python strings"""

    @wraps(f)
    def inner(*args):
        return ffi.string(f(*args))

    return inner


ffi.cdef("""
    struct _MagickWand; typedef struct _MagicWand MagickWand;
    typedef enum { ... } ExceptionType;
    typedef enum { ... } FilterTypes;

    void InitializeMagick( const char *path );

    char *MagickGetException( const MagickWand *wand, ExceptionType *severity );

    MagickWand *NewMagickWand( void );
    MagickWand *CloneMagickWand( const MagickWand *wand );
    void DestroyMagickWand( MagickWand *wand );

    unsigned int MagickStripImage( MagickWand *wand );

    unsigned int MagickReadImage( MagickWand *wand, const char *filename );
    unsigned int MagickReadImageBlob( MagickWand *wand, const unsigned char *blob, const size_t length );
    unsigned int MagickReadImageFile( MagickWand *wand, FILE *file );

    unsigned long MagickGetImageHeight( MagickWand *wand );
    unsigned long MagickGetImageWidth( MagickWand *wand );

    const char *MagickGetImageFormat( MagickWand *wand );
    unsigned int MagickSetImageFormat( MagickWand *wand, const char *format );
    unsigned int MagickSetCompressionQuality( MagickWand *wand, const unsigned long quality );

    unsigned int MagickWriteImage( MagickWand *wand, const char *filename );
    unsigned int MagickWriteImagesFile( MagickWand *wand, FILE *file, const unsigned int adjoin );
    unsigned char *MagickWriteImageBlob( MagickWand *wand, size_t *length );
    unsigned int MagickWriteImageFile( MagickWand *wand, FILE *file );

    unsigned int MagickScaleImage( MagickWand *wand, const unsigned long columns, const unsigned long rows );
    unsigned int MagickResizeImage( MagickWand *wand, const unsigned long columns,
                                    const unsigned long rows, const FilterTypes filter,
                                    const double blur );
    unsigned int MagickCropImage( MagickWand *wand, const unsigned long width,
                                  const unsigned long height, const long x, const long y );
""")


def pkgconfig(*packages, **kw):
    # See http://code.activestate.com/recipes/502261-python-distutils-pkg-config/
    from subprocess import check_output

    flag_map = {'-I': 'include_dirs',
                '-L': 'library_dirs',
                '-l': 'libraries'}

    cmd = ["pkg-config", "--libs", "--cflags"]
    cmd.extend(packages)

    for token in check_output(cmd).split():
        flag = token[:2]
        if flag in flag_map:
            kw.setdefault(flag_map.get(flag), []).append(token[2:])
        else:
            # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)

    # Remove duplicates:
    for k, v in kw.iteritems():
        kw[k] = list(set(v))

    return kw

_wand = ffi.verify("""
#include <wand/magick_wand.h>
""", **pkgconfig('GraphicsMagickWand'))

_wand.InitializeMagick(sys.argv[0])

DestroyMagickWand = _wand.DestroyMagickWand

NewMagickWand = check_rc(_wand.NewMagickWand)
CloneMagickWand = check_rc(_wand.CloneMagickWand)

MagickStripImage = check_rc(_wand.MagickStripImage)

MagickReadImage = check_rc(_wand.MagickReadImage)
MagickReadImageBlob = check_rc(_wand.MagickReadImageBlob)
MagickReadImageFile = check_rc(_wand.MagickReadImageFile)

MagickSetImageFormat = check_rc(_wand.MagickSetImageFormat)
MagickSetCompressionQuality = check_rc(_wand.MagickSetCompressionQuality)

MagickWriteImage = check_rc(_wand.MagickWriteImage)
MagickWriteImagesFile = check_rc(_wand.MagickWriteImagesFile)
MagickWriteImageFile = check_rc(_wand.MagickWriteImageFile)

MagickScaleImage = check_rc(_wand.MagickScaleImage)
MagickResizeImage = check_rc(_wand.MagickResizeImage)
MagickCropImage = check_rc(_wand.MagickCropImage)

MagickGetImageHeight = check_rc(_wand.MagickGetImageHeight)
MagickGetImageWidth = check_rc(_wand.MagickGetImageWidth)

MagickGetImageFormat = returns_string(_wand.MagickGetImageFormat)

# FIXME: figure out how to automatically populate a dict with the enum values to stay in sync with the upstream
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
