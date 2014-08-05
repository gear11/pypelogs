import logging
import argparse
import sys
import pypein
import pypef
import pypeout
from g11pyutils import StopWatch
# Execfile doesn't seem to do anything with imports,
# So add some common ones here
import hashlib
import base64

LOG = logging.getLogger("pypelogs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('specs', metavar='S', nargs='+', help='A pype specification')
    parser.add_argument("-d", "--debug", help="Log at debug level", action='store_true')
    parser.add_argument("-i", "--info", help="Log at info level", action='store_true')
    parser.add_argument("-c", "--config", help="A config file to execute")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO if args.info else logging.WARNING
    logging.basicConfig(format='%(asctime)-15s %(levelname)s:%(name)s:%(message)s', level=level, stream=sys.stderr)

    if args.config:
        LOG.info("Running config file %s" % args.config)
        execfile(args.config)

    process(args.specs)


def process(specs):
    """
    Executes the passed in list of specs
    """
    pout, pin = chain_specs(specs)
    LOG.info("Processing")
    sw = StopWatch().start()
    r = pout.process(pin)
    if r:
        print r
    LOG.info("Finished in %s", sw.read())


def chain_specs(specs):
    """
    Parses the incoming list of specs and produces a tuple (pout, pin) that can be invoked with:
        <pre>
        result = pout.process(pin)
        </pre>
    """
    LOG.info("Parsing %s specs", len(specs))
    # First spec is always an input
    pin = pypein.input_for(specs[0]).__iter__()
    # If only an input spec was provided, then use json for output
    if len(specs) == 1:
        pout = pypeout.output_for("json")
    else:
        # Middle specs are filters that successively wrap input
        for s in specs[1:-1]:
            pin = pypef.filter_for(s).filter(pin)
        # Assume output on last spec, but it may be a filter.
        # If last spec is a filter, use json for output
        try:
            pout = pypeout.output_for(specs[-1])
        except ValueError, ex:
            pin = pypef.filter_for(specs[-1]).filter(pin)
            pout = pypeout.output_for("json")
    return pout, pin


if __name__ == '__main__':
    main()