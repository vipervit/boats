#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime
from pathlib import Path

import folium
import pandas as pd
import requests

from lib.common import API_RACES, timestamp, timeago

from selenium import webdriver

url_race=API_RACES['Stardust']
html=os.path.join(str(Path.home()), 'Documents', 'boats.html')
mine='Petsamo'

res=requests.get(url_race)
boats = res.json()['result']
data=[(boats[boat]['ubtname'],
       boats[boat]['lat_dec'],
       boats[boat]['lon_dec'],
       boats[boat]['rank'],
       boats[boat]['track'],
       int(boats[boat]['timestamp']/1000))
      for boat in list(boats.keys()) if 'lat_dec' in boats[boat]]

df=pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank', 'Track', 'Timestamp'])
df['Rank']=df['Rank'].astype('int64')
df.sort_values('Rank', ascending=True, inplace=True)
df.reset_index(inplace=True)

colors=['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
        'beige', 'darkred', 'purple', 'darkpurple']

center=(df.loc[0, 'Lat'], df.loc[0, 'Lon'])

timestamp = df.loc[df.Boat == mine, 'Timestamp'].values[0]
last_updated = datetime.fromtimestamp(timestamp).strftime('%d-%h %H:%M')
updated_ago = timeago(timestamp)
hrs = str(updated_ago[0])
mins = str(updated_ago[1])
if len(hrs) < 2:
    hrs = '0' + hrs
if len(mins) < 2:
    mins = '0' + mins

title_html = '<h3 align="center" style="font-size:16px"><b>Last updated {} ({}:{} ago)</b></h3>'.format(last_updated, hrs, mins)

mymap=folium.Map(location=center, zoom_start=7)
mymap.get_root().html.add_child(folium.Element(title_html))

for idx in df.index:
    lat=df.loc[idx, 'Lat']
    lon=df.loc[idx, 'Lon']
    name=df.loc[idx, 'Boat'].upper()
    rank=df.loc[idx, 'Rank']
    if idx < len(colors):
        color=colors[idx]
    else:
        color='lightgray'
    if df.loc[idx, 'Boat']==mine:
        color='blue'
    popup=str(lat) + ', ' + str(lon)
    folium.Marker([lat, lon], popup=name + ' ' + str(rank), icon=folium.Icon(color=color, icon='sailboat', prefix='fa')).add_to(mymap)
    folium.PolyLine(df.loc[idx, 'Track'], color=color, weight=2.5, opacity=1).add_to(mymap)
mymap.save(html)

webdriver.Firefox().get('file:{}'.format(html))