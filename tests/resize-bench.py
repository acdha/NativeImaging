#!/usr/bin/env python

from collections import defaultdict
from time import time
import os
import sys

from NativeImaging import get_image_class

BACKENDS = {}
for backend_name in sys.argv[1:] or ('PIL', 'GraphicsMagick', 'Aware'):
    try:
        BACKENDS[backend_name] = get_image_class(backend_name)
    except KeyError:
        print >>sys.stderr, "Can't load %s backend" % backend_name

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "samples")
OUTPUT_DIR = os.path.join(os.environ.get("TMPDIR"), "resize-bench")

TIMES = defaultdict(dict)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print "Comparison images are saved in %s" % OUTPUT_DIR

for filename in os.listdir(SAMPLE_DIR):
    basename = os.path.splitext(filename)[0]

    for backend_name, backend_class in BACKENDS.items():
        start_time = time()

        try:
            master = backend_class.open(os.path.join(SAMPLE_DIR, filename))

            master.thumbnail((256, 256), backend_class.ANTIALIAS)

            output_file = os.path.join(OUTPUT_DIR,
                                        "%s_%s.jpg" % (basename, backend_name))

            master.save(open(output_file, "wb"), "JPEG")

            TIMES[filename][backend_name] = time() - start_time
        except StandardError, e:
            print >>sys.stderr, "%s: exception processing %s: %s" % (backend_name, filename, e)

print
print "Results"
print

for f_name, scores in TIMES.items():
    print "%s:" % f_name
    for lib, elapsed in scores.items():
        print "\t%16s: %0.2f" % (lib, elapsed)
    print