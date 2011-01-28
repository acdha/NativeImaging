import sys

from distutils.core import setup, Extension

from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, \
    DistutilsPlatformError


if sys.platform == 'win32' and sys.version_info > (2, 6):
   # 2.6's distutils.msvc9compiler can raise an IOError when failing to
   # find the compiler
   ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError,
                 IOError)
else:
   ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class BuildFailed(Exception):
    pass


class ve_build_ext(build_ext):
    # This class allows C extension building to fail.

    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError, x:
            raise BuildFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except ext_errors, x:
            raise BuildFailed()


def run_aware_setup():
   setup(name='aware',
         description = 'a python wrapper for the Aware JPEG2000 library',
         license = 'http://creativecommons.org/licenses/publicdomain/',
         version='1.0',
         ext_modules=[
           Extension('_aware',
                     ['./NativeImaging/backends/_aware.c'],
                     libraries=['awj2k'])
           ],
         cmdclass={'build_ext': ve_build_ext},
         )

if __name__=="__main__":
    try:
        run_aware_setup()
    except BuildFailed:
        print '*' * 75
        print "WARNING: Unable to install _aware"
