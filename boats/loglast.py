#! /opt/anaconda3/bin/python3

import sys

import pandas as pd

from boats.lib.boat import Boat

with Boat(sys.argv[1], getdata=False) as boat:
    boat.update_from_log()
    timestamp = boat.log.last_record.name
    s = pd.to_datetime(timestamp)
    s = s.tz_localize(tz='UTC')
    s = s.tz_convert(tz='US/Eastern')
    s = s.strftime('%d-%b %H:%M')
    print(f'{timestamp}')
    print(f'{s} EST')


