import argparse
import sys

from boats.lib.boat import Boat
from boats.lib.map import Maps


def main(args):

    map_type = None

    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--from_log', action='store_true')
    parser.add_argument('--full_info', action='store_true')

    args = parser.parse_args(args)

    with Boat(args.boat_name, getdata=False) as o_boat:
        match args.from_log:
            case True:
                o_boat.update_from_log()
            case False:
                o_boat.update_from_server(savetolog=True)
        o_boat.nav.show(args.full_info)
        if args.zoom_start is not None:
            o_boat.map.zoom = str(args.zoom_start)
        if not args.noview:
            for maptype in args.map.split(','): # TODO: fix so that no map can be specified
                o_boat.map.mtype = Maps[maptype]
                if o_boat.map.mtype == Maps.Folium:
                    hdg = o_boat.nav.az['hdg']
                    sog = o_boat.nav.speed['sog']
                    tws = o_boat.nav.wind['tws']
                    twd = o_boat.nav.wind['twd']
                    o_boat.map.boat_marker = {'hdg': hdg, 'sog': sog, 'twd': twd, 'tws': tws}
                o_boat.map.show()


if __name__ == '__main__':
    main(sys.argv[1:])
