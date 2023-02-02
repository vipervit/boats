import argparse
import sys

import boats.chartpos as chartpos
import boats.makeroutefile as makeroutefile
import boats.racemap as racemap
import boats.racemarks as racemarks
import boats.routepos as routepos


def usage():
    print('-p <boat> : Boat position and route with or without opening map')
    print('-r <boat> <race> optional: --zoom_start <n> or --noview : Race status with or '
          'without opening map')
    print('-m <race> : Get racemarks and save in CSV files')
    print('-c <boat> optional: --zoom_start <n> or --noview --full_info: Displays data and position on I-Nav maps ('
          'if no --noview')
    print('-f <boat> <file>: Makes file with coordinates to be uploaded to Sailaway. <file> is the name of the file '
          'containing exported route.')


def main(args):

    parser = argparse.ArgumentParser()
    parser.add_argument('boat_name')
    parser.add_argument('race_name')
    parser.add_argument('--routepos', action='store_true')
    parser.add_argument('--chartpos', action='store_true')
    parser.add_argument('--makeroutefile', action='store_true')
    parser.add_argument('--racemap', action='store_true')
    parser.add_argument('--racemarks', action='store_true')

    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--route_file', type=str)
    parser.add_argument('--noview', action='store_true')

    args = parser.parse_args(args)

    if args.routepos:
        routepos.main(sys.argv[2:])
    if args.chartpos:
        chartpos.main(sys.argv[2:])
    if args.makeroutefile:
        makeroutefile.main(sys.argv[2:])
    if args.racemap:
        racemap.main(sys.argv[2:])
    if args.racemarks:
        racemarks.main(sys.argv[2:])


if __name__ == "__main__":
    main(sys.argv[1:])
