from setuptools import setup
import os

from setup_aware_cext import run_aware_setup, BuildFailed

def read_file(fn):
    return open(os.path.join(os.path.dirname(__file__), fn)).read()


try:
    run_aware_setup()
except BuildFailed:
    print '*' * 75
    print "WARNING: Unable to install _aware"


setup(
    author='Chris Adams',
    author_email='chris@improbable.org',
    name='NativeImaging',
    version='0.0.6',
    url='http://github.com/acdha/NativeImaging/',
    license='http://www.opensource.org/licenses/mit-license.php',
    packages=['NativeImaging', 'NativeImaging.backends'],
    description='PIL-like interface for system imaging libraries',
    long_description=read_file("README.rst"),
)
