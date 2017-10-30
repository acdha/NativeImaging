Native Imaging
==============

This is an experiment in seeing how far you can get using platform-provided
packages such as GraphicsMagick, CoreImage, etc. to provide a PIL-like
interface but taking advantage of their support for more advanced features
such as threading, broader format support (including JPEG-2000),
vectorization, etc.

The goal is simple: a user should be able to install NativeImaging and do
something like this to a program which is currently using PIL::

    from NativeImaging import get_image_class

    Image = get_image_class("GraphicsMagick")


Status
------

.. image:: https://secure.travis-ci.org/acdha/NativeImaging.png
   :alt: Build Status
   :target: http://travis-ci.org/acdha/NativeImaging

aware
~~~~~

Very fast JPEG 2000 thumbnail generation compared to GraphicsMagick. Requires
the non-OSS AWARE library: http://www.aware.com/imaging/jpeg2000.htm

GraphicsMagick
~~~~~~~~~~~~~~

Currently supports typical web application usage: loading an image, resizing it
and saving the result. Testing reveals mixed results, beating PIL when
producing thumbnails from large TIFFs and underperforming when thumbnailing
equivalent JPEGs, both by about 2:1.

Both CPython and PyPy are supported, with PyPy seeing performance gains using the CFFI backend instead of
ctypes. Significant optimization gains are likely possible, particularly where the I/O functions marshall
data in and out of the non-filename-based APIs where data is currently being copied.

Jython
~~~~~~

Currently supports basic usage: loading an image, resizing it, and saving the
result. Performance is generally quite decent as the Java Advanced Imaging API
is quite tuned, if somewhat baroque in design.
