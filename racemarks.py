#!/usr/bin/env python
# coding: utf-8
import os
import sys
import pandas as pd
import requests

from boats import DIR_RACEMARKS
from boats.lib.common import API_RACE_MARKS, RACE_IDS


def main(racename):
    side = None

    f_racemarks = os.path.join(DIR_RACEMARKS, '{}_marks.csv'.format(racename))
    endpoint = API_RACE_MARKS.replace('RACEID', str(RACE_IDS[racename]))

    r = requests.get(endpoint)

    data = [(each['micnr'], each['miclat'], each['miclon'], each['mictypename']) for each in r.json()['missioncourse']]

    df = pd.DataFrame(data, columns=['ID', 'Lat', 'Lon', 'Description'])

    idxs = [0, 1, -2, -1]
    for i in [(df.index[idx], idx) for idx in idxs]:

        if i[1] >= 0:
            mark = 'START'
        else:
            mark = 'FINISH'
        for side in ['starboard', 'port']:
            if side in df.iloc[i[0]]['Description']:
                df.at[i[0], 'ID'] = '{} ({})'.format(mark, side)
    for i in range(2, len(df) - 2):
        for word in ['starboard', 'port']:
            if word in df.iloc[i]['Description']:
                side = word
            df.at[i, 'ID'] = 'Mark {} ({})'.format(i - 1, side)

    df.to_csv(f_racemarks)

    print('======= {} ============'.format(racename.upper()))
    print(df)


if __name__ == '__main__':
    main(sys.argv[1])
