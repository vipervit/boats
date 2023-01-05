#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import pandas as pd
import folium
import time
from datetime import datetime
import os
from pathlib import Path

url_race='https://sarl.ingenium.net.au/racelog?racenr=38602'
html=os.path.join(str(Path.home()), 'Documents', 'boats.html')
mine='Petsamo'


# In[2]:


res=requests.get(url_race)


# In[3]:


boats = res.json()['result']


# In[4]:


boats


# In[5]:


data=[(boats[boat]['ubtname'],
       boats[boat]['lat_dec'],
       boats[boat]['lon_dec'],
       boats[boat]['rank'])
      for boat in list(boats.keys()) if 'lat_dec' in boats[boat]]


# In[6]:


df=pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank'])
df['Rank']=df['Rank'].astype('int64')
df.sort_values('Rank', ascending=True, inplace=True)
df.reset_index(inplace=True)


# In[7]:


colors=['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
        'beige', 'darkred', 'purple', 'darkpurple']


# In[8]:


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


# In[10]:


mymap.save(html)

