import argparse
import sys

import boats.makeroutefile as makeroutefile
import boats.racemap as racemap
import boats.racemarks as racemarks
import boats.routepos as routepos
import boats.upcoming as upcoming
import boats.viewboat as viewboat


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument('-routepos', action='store_true')
    parser.add_argument('-makeroutefile', action='store_true')
    parser.add_argument('-racemap', action='store_true')
    parser.add_argument('-racemarks', action='store_true')
    parser.add_argument('-upcoming', action='store_true')
    parser.add_argument('-viewboat', action='store_true')

    parser.add_argument('--boat_name', type=str)
    parser.add_argument('--map', type=str)
    parser.add_argument('--race_name', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--route_file', type=str)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--step', type=int)

    args = parser.parse_args(args)

    if args.routepos:
        routepos.main(sys.argv[2:])
    if args.makeroutefile:
        makeroutefile.main(sys.argv[2:])
    if args.racemap:
        racemap.main(sys.argv[2:])
    if args.racemarks:
        racemarks.main(args.race_name)
    if args.upcoming:
        upcoming.main()
    if args.viewboat:
        viewboat.main(sys.argv[2:])


if __name__ == "__main__":
    main(sys.argv[1:])
