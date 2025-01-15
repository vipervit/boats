#! /opt/anaconda3/bin/python3

import sys

import pandas as pd

from boats.lib.boat import Boat

with Boat(sys.argv[1]) as boat:
    df = boat.get_logged_data()
    timestamp = df.index[-1]
    s = pd.to_datetime(timestamp)
    s = s.tz_localize(tz='UTC')
    s = s.tz_convert(tz='US/Eastern')
    print(df.iloc[-1])
    s = s.strftime('%d-%b %H:%M')
    print(f'Timestamp in local:\n{s} EST')


