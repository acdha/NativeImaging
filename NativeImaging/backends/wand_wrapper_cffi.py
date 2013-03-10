# encoding: utf-8
"""
cffi wrappers for GraphicsMagick functions with error-handling

n.b. Heavy consultation of http://www.graphicsmagick.org/wand/magick_wand.html
and the cffi documentation is advised
"""

import sys

from cffi import FFI

ffi = FFI()


class WandException(Exception):
    pass


def _wand_errcheck(rc, func, args):
    """
    Intended for use as a ctypes errcheck function

    Can only be used with functions which take Wand as their first argument
    """

    if not rc:
        err_type = ffi.new("int", 0)
        description = wand.MagickGetException(args[0], err_type)

        if err_type.value == 430:  # "Unable to open file"
            raise IOError(description)
        else:
            raise WandException(description)
    else:
        return rc


ffi.cdef("""
    struct _MagickWand { ...; };

    typedef struct _MagickWand MagickWand;
    typedef enum { ... } ExceptionType;
    typedef enum { ... } FilterTypes;

    char *MagickGetException( const MagickWand *wand, ExceptionType *severity );

    MagickWand NewMagickWand( void );
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

wand = ffi.verify("""
#include <wand/magick_wand.h>
""", **pkgconfig('GraphicsMagickWand'))

# FIXME: update _wand_errcheck to decorate wand.* for functions in cdefs

wand.InitializeMagick(sys.argv[0])
