Native Imaging
==============

This is an experiment in seeing how far you can get using platform-provided
packages such as GraphicsMagick, CoreImage, etc. to provide a PIL-like
interface but taking advantage of their support for more advanced features
such as threading, broader format support (including JPEG-2000),
vectorization, etc.

The goal is simple: a user should be able to install NativeImaging and do
something like this to a program which is currently using PIL::

    from NativeImaging.backends.GraphicsMagick import GraphicsMagickImage as Image

Status
------

Currently only the most basic use-case is supported: loading an image,
resizing it and saving the result. Testing reveals mixed results, beating PIL
when producing thumbnails from large TIFFs and underperforming when
thumbnailing equivalent JPEGs, both by about 2:1. Further profiling is
warranted.
