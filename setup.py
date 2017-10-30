# encoding: utf-8
from __future__ import absolute_import, division, print_function

from setuptools import setup
import os


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    author='Chris Adams',
    author_email='chris@improbable.org',
    name='NativeImaging',
    use_scm_version=True,
    url='http://github.com/acdha/NativeImaging/',
    license='http://www.opensource.org/licenses/mit-license.php',
    description='PIL-like interface for system imaging libraries',
    long_description=read_file("README.rst"),
    packages=['NativeImaging', 'NativeImaging.backends'],
    test_suite='tests',
    setup_requires=['setuptools_scm'],
)
