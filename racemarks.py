#!/usr/bin/env python
# coding: utf-8
import requests
import sys
import pandas as pd

from lib.common import *

racename = sys.argv[1]
endpoint=API_RACE_MARKS.replace('RACEID', str(RACE_IDS[racename]))
r = requests.get(endpoint)                                

data=[(each['micnr'], each['miclat'], each['miclon'], each['mictypename']) for each in r.json()['missioncourse']]

df=pd.DataFrame(data, columns=['ID', 'Lat', 'Lon', 'Description'])

idxs = [0, 1, -2, -1]
for i in [(df.index[idx],idx)  for idx in idxs]:
    if i[1] >= 0:
        mark = ' START '
    else:
        mark = ' FINISH'
    for side in ['starboard', 'port']:
        if side in df.iloc[i[0]]['Description']:
            if side == 'port':
                side += '     '
            df.at[i[0], 'ID'] = '{} ({})'.format(mark, side)
for i in range(2, len(df)-2):
    for word in ['starboard', 'port']:
        if word in df.iloc[i]['Description']:
            side = word
            if side == 'port':
                side += '     '
        if i < 10:
            ws = ' '
        else:
            ws=''
        df.at[i, 'ID'] = 'MRK{} {} ({})'.format(ws, i, side)

df.drop('Description', axis=1, inplace=True)

print('======= {} ============'.format(racename.upper()))
print(df)

