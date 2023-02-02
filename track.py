#!/usr/bin/env python
# coding: utf-8


import os
import sys
import webbrowser
from datetime import datetime

import folium
import pandas as pd
from folium.plugins import BoatMarker

from boats import DIR_HTML, DIR_SAILDATA
from boats.lib.boat import Boat
from boats.lib.common import MY_USER, get_boat_race_data

boat_name = sys.argv[1]
launch_browser = sys.argv[2]

user = MY_USER
html = os.path.join(DIR_HTML, '{}.html'.format(boat_name))
f_data = os.path.join(DIR_SAILDATA, '{}_dat.json'.format(boat_name))

timestamp = datetime.now().strftime('%d-%b %H:%M')

oBoat = Boat(boat_name)
oBoat.getdata()
curr_pos = [round(oBoat.pos[0], 3), round(oBoat.pos[1], 3)]
sog = oBoat.nav['sog']
hdg = oBoat.nav['hdg']

track = Boat(boat_name).get_track_from_log()

title_html = '<h3 align="center" style="font-size:16px">{}                  lat:{}, lon:{}     {}°    {} kn<b></b></h3>'. \
    format(timestamp, curr_pos[0], curr_pos[1], hdg, sog)

mymap = folium.Map(location=curr_pos, zoom_start=7)
mymap.get_root().html.add_child(folium.Element(title_html))

folium.PolyLine(track).add_to(mymap)
BoatMarker(curr_pos, color='blue',
           heading=oBoat.nav['hdg'],
           wind_heading=oBoat.wind['twd'],
           wind_speed=oBoat.wind['tws']
           ).add_to(mymap)

mymap.save(html)

if launch_browser == 'True':
    webbrowser.open('file:{}'.format(html))
