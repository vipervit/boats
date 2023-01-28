import os
import sys
from datetime import datetime
import geopy.distance

import folium
import pandas as pd
from folium.plugins import BoatMarker

from boats.lib.boat import Boat
from boats.lib.common import DIR_HOME
from boats.lib.common import DIR_HTML

boat_name = sys.argv[1]
fn_route = sys.argv[2]
zoom_start = sys.argv[3]

fn_map = '{}.html'.format(boat_name)

f_map = os.path.join(DIR_HTML, fn_map)
f_json = os.path.join(DIR_HOME, 'routes', 'exported', '{}.json'.format(fn_route))

df = pd.read_json(f_json)
df.columns = ['Name', 'Points']
df.drop('Name', axis=1, inplace=True)
df.drop(0, axis=0, inplace=True)
df['epoch'] = [df['Points'][idx][0] for idx in df.index]
df['Lon'] = [float(df['Points'][idx][1])/1000 for idx in df.index]
df['Lat'] = [float(df['Points'][idx][2])/1000 for idx in df.index]
df.drop('Points', axis=1, inplace=True)
df['epoch'] = df['epoch'].astype(int)
df['ETA'] = [datetime.fromtimestamp(x).strftime("%d-%h %H:%M") for x in df['epoch']]
df.drop('epoch', axis=1, inplace=True)

mymap = folium.Map(location=[df.iloc[1]['Lat'], df.iloc[1]['Lon']], zoom_start=zoom_start)

# boat
oBoat = Boat(boat_name)
oBoat.getdata()
curr_pos = [round(oBoat.pos[0], 3), round(oBoat.pos[1], 3)]
sog = oBoat.nav['sog']
hdg = oBoat.nav['hdg']
popup = '{},{} {}° {} kn'.format(curr_pos[0], curr_pos[1], hdg, sog)

BoatMarker(curr_pos, color='blue',
           heading=oBoat.nav['hdg'],
           wind_heading=oBoat.wind['twd'],
           wind_speed=oBoat.wind['tws'],
           popup=popup).add_to(mymap)

# route line
points = [(df.iloc[i]['Lat'], df.iloc[i]['Lon']) for i in range(len(df.index))]
folium.PolyLine(points, color='red').add_to(mymap)

# route points
markers = [(i+1, df.iloc[i]['Lat'], df.iloc[i]['Lon'],) for i in range(len(df.index))]

for i in range(len(markers)):
    name = markers[i][0]
    lat = markers[i][1]
    lon = markers[i][2]
    dist = round(geopy.distance.geodesic((lat, lon), curr_pos).nm)
    popup = '{} {},{} {} nm {} hrs'.format(name, round(lat, 3), round(lon, 3), dist, round(dist/sog))
    folium.Marker([lat, lon], popup=popup).add_to(mymap)

mymap.save(f_map)
