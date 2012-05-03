#!/usr/bin/env python
"""Compare performance of the available backends
"""
from collections import defaultdict
from optparse import OptionParser
from time import time
import logging
import os
import sys
import tempfile

from NativeImaging import get_image_class


def main():
    parser = OptionParser()
    parser.add_option("-v", default=0, dest="verbosity", action="count")
    parser.add_option('--sample-dir',
                      default=os.path.join(os.path.dirname(__file__),
                                           "samples"),
                      help="Path to test images (default: %default)")
    parser.add_option('--output-dir',
                      default=os.path.join(tempfile.gettempdir(),
                                           "resize-bench"),
                      help="Path to store output images (default:  %default)")

    (options, backend_names) = parser.parse_args()

    if options.verbosity > 1:
        log_level = logging.DEBUG
    elif options.verbosity > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s",
                        level=log_level)

    return run_benchmark(backend_names, sample_dir=options.sample_dir,
                         output_dir=options.output_dir)


def run_benchmark(backend_names, sample_dir=None, output_dir=None):
    if not backend_names:
        backend_names = ('PIL', 'GraphicsMagick', 'Aware', 'java')

    backends = {}

    for backend_name in backend_names:
        try:
            backends[backend_name] = get_image_class(backend_name)
        except (ImportError, KeyError):
            print >> sys.stderr, "Can't load %s backend" % backend_name

    times = defaultdict(dict)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print "Comparison images are saved in %s" % output_dir

    for filename in os.listdir(sample_dir):
        if filename.startswith("."):
            continue

        basename = os.path.splitext(filename)[0]

        for backend_name, backend_class in backends.items():
            logging.info("Resizing %s using %s", filename, backend_name)
            start_time = time()

            try:
                master = backend_class.open(os.path.join(sample_dir, filename))

                master.thumbnail((256, 256), backend_class.ANTIALIAS)

                output_file = os.path.join(output_dir,
                                           "%s_%s.jpg" % (basename, backend_name))

                master.save(open(output_file, "wb"), "JPEG")

                times[filename][backend_name] = time() - start_time

            # This allows us to use a blanket except below which has the nice
            # property of catching direct Exception subclasses and things like
            # java.lang.Exception subclasses on Jython:
            except SystemExit:
                sys.exit(1)
            except:
                logging.exception("%s: exception processing %s", backend_name,
                                  filename)

    print
    print "Results"
    print

    for f_name, scores in times.items():
        print "%s:" % f_name
        for lib, elapsed in scores.items():
            print "\t%16s: %0.2f" % (lib, elapsed)
        print

if __name__ == "__main__":
    main()