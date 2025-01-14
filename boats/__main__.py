import argparse
import sys

import boatmonitor
import boats.viewboat as viewboat


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewboat', action='store_true')
    parser.add_argument('--boat_name', type=str)
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--monitor', action='store_true')

    args = parser.parse_args(args)

    if args.viewboat:
        viewboat.main(sys.argv[2:])
    if args.monitor:
        boatmonitor.main(['--boat_name', args.boat_name])


if __name__ == "__main__":
    main(sys.argv[1:])
