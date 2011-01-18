from setuptools import setup

setup(
    author='Chris Adams',
    author_email='chris@improbable.org',
    name='NativeImaging',
    version='0.0.1',
    url='http://acdha.github.com/NativeImaging/',
    license='http://www.opensource.org/licenses/mit-license.php',
    packages=['NativeImaging', 'NativeImaging.backends'],
    description='PIL-like interface using existing libraries such as GraphicsMagick or CoreImage',
)
