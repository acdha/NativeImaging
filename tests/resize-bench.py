#!/usr/bin/env python

from collections import defaultdict
from time import time
import os
import sys

from PIL import Image as PILImage
from NativeImaging.backends.GraphicsMagick import GraphicsMagickImage as MagickImage

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "samples")
OUTPUT_DIR = os.path.join(os.environ.get("TMPDIR"), "resize-bench")

TIMES = defaultdict(dict)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print "Comparison images are saved in %s" % OUTPUT_DIR

for filename in os.listdir(SAMPLE_DIR):
    basename = os.path.splitext(filename)[0]

    try:
        # PIL Baseline:
        start_time = time()

        master = PILImage.open(os.path.join(SAMPLE_DIR, filename))

        master.thumbnail((256, 256), PILImage.ANTIALIAS)

        master.save(open(os.path.join(OUTPUT_DIR, "%s_PIL.jpg" % basename), "wb"), "JPEG")

        TIMES[filename]['PIL'] = time() - start_time
    except StandardError, e:
        print >>sys.stderr, "PIL: Unhandled exception processing %s: %s" % (filename, e)

    try:
        # Graphics Magick:
        start_time = time()

        master = MagickImage.open(os.path.join(SAMPLE_DIR, filename))

        master.thumbnail((256, 256), MagickImage.ANTIALIAS)

        # master.save(open(os.path.join(OUTPUT_DIR, "%s_graphicsmagick.jpg" % basename), "wb"), "JPEG")
        master.save(os.path.join(OUTPUT_DIR, "%s_graphicsmagick.jpg" % basename), "JPEG")

        TIMES[filename]['GraphicsMagick'] = time() - start_time
    except StandardError, e:
        print >>sys.stderr, "GraphicsMagick: Unhandled exception processing %s: %s" % (filename, e)

print
print "Results"
print

for f_name, scores in TIMES.items():
    print "%s:" % f_name
    for lib, elapsed in scores.items():
        print "\t%16s: %0.2f" % (lib, elapsed)