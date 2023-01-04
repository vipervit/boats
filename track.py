#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import pandas as pd
import folium
import time
import os
from pathlib import Path

url_race='https://sarl.ingenium.net.au/racelog?racenr=38602'
url_boat='http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key=7B79EE2988A44080A37C06570F4B5EE8'
user='Viper Vit'
boat='Petsamo'
html=os.path.join(str(Path.home()), 'Documents', boat + '.html')


# In[2]:


timestamp=time.time()


# In[3]:


user_fleet=requests.get(url_boat)


# In[4]:


for each in user_fleet.json():
    name=each['boatname']
    if name==boat:
        lat=round(each['latitude'],3)
        lon=round(each['longitude'],3)
curr_pos=[lat, lon]
curr_pos


# In[5]:


res=requests.get(url_race)


# In[6]:


boats = res.json()['result']


# In[7]:


boat_data = boats[user + '-' + boat]


# In[8]:


boat_data


# In[9]:


#print('Last update: {}'.format(time.ctime(boat_data['timestamp'])))


# In[10]:


track=boat_data['track']
track.reverse()
track.append(curr_pos)
track


# In[11]:


df_track=pd.DataFrame(track)
df_track.columns=['Lat', 'Lon']
df_track


# In[12]:


list(df_track.index)


# In[13]:


center=(track[0][0], track[0][1])
mymap=folium.Map(location=center, zoom_start=7)
for idx in df_track.index:
    lat=df_track.loc[idx, 'Lat']
    lon=df_track.loc[idx, 'Lon']
    popup=str(lat) + ', ' + str(lon)
    if idx==df_track.index.max():
        popup=time.ctime(timestamp) + ' ' + popup
    folium.Marker([lat, lon], popup=popup).add_to(mymap)
mymap


# In[14]:


mymap.save(html)

