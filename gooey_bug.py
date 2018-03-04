import argparse
from gooey import Gooey
from gooey import GooeyParser

@Gooey
def main():
    parser = GooeyParser(description="Convert python to rpn for hp41s/free42/dm42")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    parser.add_argument('filename', help="name of the file to process", widget='FileChooser')
    parser.add_argument("-n", "--nolinenum", action='store_true', help="do not generate line numbers")
    parser.add_argument("-c", "--comments", action='store_true', help="generate commants")
    args = parser.parse_args()

    def run():
        print('work done here...')

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
