#! /opt/anaconda3/bin/python3

import sys

from boats.lib.boat import Boat

with Boat(sys.argv[1]) as boat:
    print(boat.get_logged_data())
