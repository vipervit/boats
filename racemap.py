#!/usr/bin/env python
# coding: utf-8

import os
import sys
import webbrowser
from datetime import datetime

import folium
import pandas as pd
from folium.plugins import BoatMarker

from lib.common import timeago, DIR_HTML, get_race_data

myboat = sys.argv[1].upper()
race = sys.argv[2]
launch_browser = sys.argv[3]
html = os.path.join(DIR_HTML, '{}.html'.format(race))
zoom_start = 7

boats = get_race_data(race)

data = [(boats[boat]['ubtname'].upper(),
         boats[boat]['lat_dec'],
         boats[boat]['lon_dec'],
         boats[boat]['rank'],
         boats[boat]['track'],
         int(boats[boat]['timestamp'] / 1000),
         boats[boat]['heading'],
         boats[boat]['lastreport_speed'],
         boats[boat]['wind'].split(',')[0].strip('°'),
         boats[boat]['wind'].split(',')[1].strip().strip('kn.'),
         boats[boat]['resultdescr'].split(',')[3].split('nm')[0].split('.')[0].strip())
        for boat in list(boats.keys()) if 'lat_dec' in boats[boat]]

df = pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank', 'Track', 'Timestamp', 'HDG', 'SPD', 'TWD', 'TWS', 'DTW'])
df['Rank'] = df['Rank'].astype(int)
df=df.set_index('Rank')
df.sort_values('Rank', ascending=True, inplace=True)
timestamp = df.loc[df.Boat == myboat, 'Timestamp'].values[0] # must be before the next line
df.at[df[df['Boat'] == myboat].index[0], 'Boat'] = '<======= ' + myboat + ' =======>'

behind = abs(float(df[df.index==1]['DTW'][1]) - float(df[df['Boat'].str.contains(myboat)]['DTW'].values[0]))

print(df[['Boat', 'SPD', 'TWS', 'DTW']])
print('')
print('Behind leader by: {} nm'.format(round(behind),2))

colors = ['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
          'beige', 'darkred', 'purple', 'darkpurple']

center = (df.loc[df.index == 1, 'Lat'], df.loc[df.index == 1, 'Lon'])

last_updated = datetime.fromtimestamp(timestamp).strftime('%d-%h %H:%M')
updated_ago = timeago(timestamp)
hrs = str(updated_ago[0])
mins = str(updated_ago[1])
if len(hrs) < 2:
    hrs = '0' + hrs
if len(mins) < 2:
    mins = '0' + mins

title_html = '<h3 align="center" style="font-size:16px"><b>Last updated {} ({}:{} ago)</b></h3>'.format(last_updated,
                                                                                                        hrs, mins)

mymap = folium.Map(location=center, zoom_start=zoom_start)
mymap.get_root().html.add_child(folium.Element(title_html))

for idx in df.index:
    lat = df.loc[idx, 'Lat']
    lon = df.loc[idx, 'Lon']
    name = df.loc[idx, 'Boat'].upper()
    rank = idx
    track = df.loc[idx, 'Track']
    spd = df.loc[idx, 'SPD']
    hdg = df.loc[idx, 'HDG']
    twd = df.loc[idx, 'TWD']
    tws = df.loc[idx, 'TWS']
    if idx < len(colors):
        color = colors[idx - 1]
    else:
        color = 'lightgray'
    if myboat in df.loc[idx, 'Boat']:
        name = myboat
        color = 'blue'
    popup = '{} rank: {} {} kn'.format(name, str(rank), spd)

    BoatMarker([lat, lon], color=color,
               heading=hdg,
               wind_heading=twd,
               wind_speed=tws,
               popup=popup).add_to(mymap)
    folium.PolyLine(track, color=color, weight=2.5, opacity=1).add_to(mymap)

mymap.save(html)

if launch_browser == '1':
    webbrowser.open('file:{}'.format(html))
