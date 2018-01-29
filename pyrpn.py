import argparse
from parse import parse
import logging
from logger import config_log
# from gooey import Gooey

log = logging.getLogger(__name__)
config_log(log)

# @Gooey
def main():
    parser = argparse.ArgumentParser(description="Convert python to rpn for hp41s/free42/dm42")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("filename", type=str, help="the filename")
    parser.add_argument("-n", "--nolinenum", action='store_true', help="do not generate line numbers")
    parser.add_argument("-c", "--comments", action='store_true', help="generate commants")
    args = parser.parse_args()

    # pprint.pprint(args, indent=4)

    def run():
        with open(args.filename) as fp:
            source = fp.read()
        program = parse(source)
        rpn = program.lines_to_str(comments=args.comments, linenos=not args.nolinenum)

        if args.quiet:
            print(rpn)
        elif args.verbose:
            print('source is', source)
            print('rpn is', rpn)
        else:
            line_count = len(rpn.split('\n'))
            print(f'Generated {line_count} lines.')
            print(rpn)

    run()

main()
