import argparse
import sys

import boats.makeroutefile as makeroutefile
import boats.viewboat as viewboat


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument('-routepos', action='store_true')
    parser.add_argument('-makeroutefile', action='store_true')
    parser.add_argument('-viewboat', action='store_true')
    parser.add_argument('--boat_name', type=str)
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--route_name', type=str)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--step', type=int)

    args = parser.parse_args(args)

    if args.makeroutefile:
        makeroutefile.main(sys.argv[2:])
    if args.viewboat:
        viewboat.main(sys.argv[2:])


if __name__ == "__main__":
    main(sys.argv[1:])
