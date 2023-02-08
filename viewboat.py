import argparse
import sys
import webbrowser

from boats.lib.boat import Boat
from boats.lib.common import DEFAULT_ZOOM, make_windy_url, URL_IBOATING_CHART


def main(args):

    zoom_start = str(DEFAULT_ZOOM)

    parser = argparse.ArgumentParser(description='Displays the current boat position, sails, nav, and other data.')
    parser.add_argument('--boat_name')
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--full_info', action='store_true')

    args = parser.parse_args(args)

    with Boat(args.boat_name) as o_boat:
        o_boat.getdata()
        o_boat.show(args.full_info)
        lat = o_boat.pos[0]
        lon = o_boat.pos[1]

    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)

    if args.map == 'Windy':
            url = make_windy_url(lat, lon, zoom_start)
    if args.map == 'I-Boating':
            url = '{}#{}/{}/{}'.format(URL_IBOATING_CHART, zoom_start, lat, lon)

    if not args.noview:
        webbrowser.open(url)


if __name__ == '__main__':
    main(sys.argv[1:])
