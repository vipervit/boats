#!/usr/bin/env python
# coding: utf-8

import os
from pathlib import Path

import folium
import pandas as pd
import requests

from lib.common import API_RACES

url_race=API_RACES['Stardust']
html=os.path.join(str(Path.home()), 'Documents', 'boats.html')
mine='Petsamo'

res=requests.get(url_race)
boats = res.json()['result']
data=[(boats[boat]['ubtname'],
       boats[boat]['lat_dec'],
       boats[boat]['lon_dec'],
       boats[boat]['rank'])
      for boat in list(boats.keys()) if 'lat_dec' in boats[boat]]

df=pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank'])
df['Rank']=df['Rank'].astype('int64')
df.sort_values('Rank', ascending=True, inplace=True)
df.reset_index(inplace=True)

colors=['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
        'beige', 'darkred', 'purple', 'darkpurple']

center=(df.loc[0, 'Lat'], df.loc[0, 'Lon'])
mymap=folium.Map(location=center, zoom_start=7)
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
        color='lightblue'
    popup=str(lat) + ', ' + str(lon)
    folium.Marker([lat, lon], popup=name + ' ' + str(rank), icon=folium.Icon(color=color, icon='sailboat', prefix='fa')).add_to(mymap)
mymap.save(html)

