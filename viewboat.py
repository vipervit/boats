import argparse
import sys

from boats.lib.boat import Boat
from boats.lib.common import Maps


def main(args):

    map_type = None

    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--full_info', action='store_true')

    args = parser.parse_args(args)

    if args.map is not None:
        map_type = Maps[args.map]

# TODO: add point of sail
    with Boat(args.boat_name) as o_boat:
        o_boat.get_data()
        o_boat.map.mtype = map_type
        o_boat.show(args.full_info)
        if args.zoom_start is not None:
            o_boat.map.zoom = str(args.zoom_start)
        if not args.noview:
            if map_type == Maps.Folium:
                hdg = o_boat.nav['hdg']
                sog = o_boat.nav['sog']
                tws = o_boat.wind['tws']
                twd = o_boat.wind['twd']
                o_boat.map.track = o_boat.get_track()
                o_boat.map.boat_marker = {'hdg': hdg, 'sog': sog, 'twd': twd, 'tws': tws}
            o_boat.map.show()


if __name__ == '__main__':
    main(sys.argv[1:])
