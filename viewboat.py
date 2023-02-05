import argparse
import sys

from boats.lib.boat import Boat


def main(args):
    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    parser.add_argument('--full_info', action='store_true')
    args = parser.parse_args(args)

    with Boat(args.boat_name) as o_boat:
        o_boat.getdata()
        o_boat.show(args.full_info)


if __name__ == '__main__':
    main(sys.argv[1:])
