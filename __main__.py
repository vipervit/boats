import argparse
import getopt
import sys

import boats.racemap as racemap
import boats.route_pos as route_pos
import boats.racemarks as racemarks
import boats.chart_pos as chart_pos
import boats.route_file as route_file
from boats.lib.common import DEFAULT_ZOOM


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

    zoom_start = str(DEFAULT_ZOOM)

    parser = argparse.ArgumentParser()
    parser.add_argument('boat_name')
    parser.add_argument('--racemap', action='store_true')
    parser.add_argument('--chart', action='store_true')
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--route_file', type=str)
    parser.add_argument('--noview', action='store_true')
    args = parser.parse_args(args)
    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)

    #route_pos.main(args)
    if args.racemap:
        racemap.main(args)
    #racemarks.main(args[0])
    if args.chart:
        chart_pos.main(args)
    #route_file.main(args)


if __name__ == "__main__":
    main(sys.argv[1:])
