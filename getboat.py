#! /opt/anaconda3/bin/python3

import sys
import datetime
import time

from boats.lib.boat import Boat

dir_log = '/Users/hedge/'
f_log = dir_log + 'getboat.log'
boat_name = sys.argv[1]

if len(sys.argv) < 3:
    interval = 600
else:
    interval = sys.argv[2]

while True:
    with Boat(boat_name) as boat:
        with open(f_log, 'a') as f:
            f.write(boat_name + ' ' + datetime.datetime.now().strftime('%d-%b %H:%M') + '\n')
        data = boat.get_data()
    time.sleep(int(interval))
