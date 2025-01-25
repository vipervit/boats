import argparse
import os
import shutil
import sys

from boats import boatmonitor
from boats import viewboat as viewboat
from boats.lib.boat import Boat
from boats.lib.common import get_version_from_pyproject
from boats.lib.dest import Destinations


def add_destination(params):
    place, coors = params[0], [params[1], params[2]]
    Destinations().add_new(place, coors)


def remove_destination(name):
    Destinations().remove(name)


def view_destinations():
    Destinations().view()


def copy_log(boatname, destdir):
    logfile = Boat(boatname).log.myfile
    dest_fname = logfile.split(os.sep)[-1]
    shutil.copy(logfile, os.path.join(destdir, dest_fname))


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--viewboat', action='store_true')
    parser.add_argument('--boat_name', type=str)
    parser.add_argument('--map', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--full_info', action='store_true')
    parser.add_argument('--noview', action='store_true')
    parser.add_argument('--monitor', action='store_true')
    parser.add_argument('--destination', action='store_true')
    parser.add_argument('--add', type=str)
    parser.add_argument('--remove', type=str)
    parser.add_argument('--view', action='store_true')
    parser.add_argument('--copy_log', action='store_true')
    parser.add_argument('--todir', type=str)
    parser.add_argument('--from_log', action='store_true')
    parser.add_argument('--version', action='store_true')

    args = parser.parse_args(args)

    if args.viewboat:
        viewboat.main(sys.argv[2:])
    if args.monitor:
        boatmonitor.main(['--boat_name', args.boat_name])
    if args.destination:
        if args.add is not None:
            add_destination(args.add.split(','))
            view_destinations()
        if args.remove is not None:
            remove_destination(args.remove)
            view_destinations()
        if args.view:
            view_destinations()
    if args.copy_log:
        copy_log(args.boat_name, args.todir)
    if args.version:
        print(get_version_from_pyproject())


if __name__ == "__main__":
    main(sys.argv[1:])
