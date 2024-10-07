#! /opt/anaconda3/bin/python3

import sys
import time

from boats.lib.boat import Boat

boat_name = sys.argv[1]

if len(sys.argv) < 3:
    interval = 600
else:
    interval = sys.argv[2]

while True:
    with Boat(boat_name) as boat:
        boat.get_data()
    time.sleep(int(interval))
