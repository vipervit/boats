#!/usr/bin/env python
# coding: utf-8


import os
import sys
import webbrowser
from datetime import datetime

import folium
import pandas as pd
from folium.plugins import BoatMarker

from lib.boat import boat
from lib.common import DIR_SAILDATA, MY_USER, get_boat_race_data, DIR_HTML

boatname = sys.argv[1]
race = sys.argv[2]
launch_browser = sys.argv[3]

user=MY_USER
html=os.path.join(DIR_HTML, boatname + '.html')

timestamp=datetime.now().strftime('%d-%b %H:%M')

oBoat = boat(boatname)
oBoat.getdata()
curr_pos = [round(oBoat.pos[0],3), round(oBoat.pos[1],3)]
sog = oBoat.nav['sog']
hdg = oBoat.nav['hdg']

race_data = get_boat_race_data(race, user, boatname)
rank = race_data['rank']
track = race_data['track']
track.reverse()
track.append(curr_pos)

df_track=pd.DataFrame(track)
df_track.columns=['Lat', 'Lon']

title_html = '<h3 align="center" style="font-size:16px">{}                  {},{}     {}°    {} kn<b></b></h3>'.\
    format(timestamp, curr_pos[0], curr_pos[1], hdg, sog)

mymap=folium.Map(location=curr_pos, zoom_start=7)
mymap.get_root().html.add_child(folium.Element(title_html))
popup='rank: {}'.format(rank)

folium.PolyLine(track).add_to(mymap)
BoatMarker(curr_pos, color='blue',
           heading=oBoat.nav['hdg'],
           wind_heading=oBoat.wind['twd'],
           wind_speed=oBoat.wind['tws'],
           popup=popup).add_to(mymap)

mymap.save(html)

if launch_browser == '1':
    webbrowser.open('file:{}'.format(html))