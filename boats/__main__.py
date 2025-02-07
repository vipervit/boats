import argparse
import os
import shutil
import sys

from boats import boatmonitor, DIR_LOGS
from boats import viewboat as viewboat
from boats.lib.boat import Boat
from boats.lib.common import get_version_from_pyproject, make_log_file_name
from boats.lib.dest import Destinations


def add_destination(params):
    place, coors = params[0], [params[1], params[2]]
    Destinations().add_new(place, coors)


def remove_destination(name):
    Destinations().remove(name)


def view_destinations():
    Destinations().view()


def copy_log(boatname, outdir, action):
    src, dest = None, None
    fname = make_log_file_name(boatname)
    inloc = os.path.join(DIR_LOGS, fname)
    outloc = os.path.join(outdir, fname)
    match action:
        case 'install':
            src = outloc
            dest = inloc
        case 'backup':
            src = inloc
            dest = outloc
    shutil.copy(src, dest)


def view_log_last(boatname):
    with Boat(boatname, getdata=False) as boat:
        boat.update_from_log()
        print(boat.log.last_record_timestamp)
        print(f'{boat.log.last_record_timestamp_local} EST')


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
    parser.add_argument('--log', action='store_true')
    parser.add_argument('--backup', action='store_true')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--viewlast', action='store_true')
    parser.add_argument('--dir', type=str)
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
    if args.log:
        if args.install:
            copy_log(args.boat_name, args.dir, action='install')
        if args.backup:
            copy_log(args.boat_name, args.dir, action='backup')
        if args.viewlast:
            view_log_last(args.boat_name)

    if args.version:
        print(get_version_from_pyproject())


if __name__ == "__main__":
    main(sys.argv[1:])
