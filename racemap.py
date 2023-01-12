#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime
from pathlib import Path

import folium
import pandas as pd
import requests

from lib.common import API_RACES, timestamp

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
       datetime.fromtimestamp(boats[boat]['timestamp']/1000).strftime('%d-%h %H:%M'))
      for boat in list(boats.keys()) if 'lat_dec' in boats[boat]]

df=pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank', 'Track', 'As of'])
df['Rank']=df['Rank'].astype('int64')
df.sort_values('Rank', ascending=True, inplace=True)
df.reset_index(inplace=True)

colors=['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
        'beige', 'darkred', 'purple', 'darkpurple']

center=(df.loc[0, 'Lat'], df.loc[0, 'Lon'])

last_updated = df.loc[df.Boat == mine, 'As of'].values[0]

title_html = '<h3 align="center" style="font-size:16px"><b>Last updated: {}</b></h3>'.format(last_updated)

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