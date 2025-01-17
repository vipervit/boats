#! /opt/anaconda3/bin/python3

import sys

from boats.lib.boat import Boat

with Boat(sys.argv[1], getdata=False) as boat:
    boat.update_from_log()
    print(boat.log.last_record_timestamp)
    print(f'{boat.log.last_record_timestamp_local} EST')
