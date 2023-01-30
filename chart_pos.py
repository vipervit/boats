import sys
import webbrowser
import argparse

from boats.lib.common import Boat, DEFAULT_ZOOM, URL_IBOATING_CHART, timestamp


def main(args):

    zoom_start = str(DEFAULT_ZOOM)

    parser = argparse.ArgumentParser(description='Displays the current boat position on I-Nav map.')
    parser.add_argument('boat_name')
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--full_info', action='store_true')
    args = parser.parse_args(args)
    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)

    url = '{}#ZOOM/LAT/LON'.format(URL_IBOATING_CHART)
    o_boat = Boat(args.boat_name)
    o_boat.getdata()
    pos = o_boat.pos
    if not args.noview:
        url = url.replace('LAT', str(round(pos[0], 4)))
        url = url.replace('LON', str(round(pos[1], 4)))
        url = url.replace('ZOOM', zoom_start)
        webbrowser.open(url)
    o_boat.show(args.full_info)
    print('\n{}'.format(timestamp()))


if __name__ == '__main__':
    main(sys.argv[1:])
