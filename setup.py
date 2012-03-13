from setuptools import setup

from setup_aware_cext import run_aware_setup, BuildFailed

try:
    run_aware_setup()
except BuildFailed:
    print '*' * 75
    print "WARNING: Unable to install _aware"


setup(
    author='Chris Adams',
    author_email='chris@improbable.org',
    name='NativeImaging',
    version='0.0.5',
    url='http://github.com/acdha/NativeImaging/',
    license='http://www.opensource.org/licenses/mit-license.php',
    packages=['NativeImaging', 'NativeImaging.backends'],
    description='PIL-like interface using existing libraries such as GraphicsMagick or CoreImage',
)
