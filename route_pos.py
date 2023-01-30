import argparse
import os
import sys
import webbrowser
from datetime import datetime

import folium
import geopy.distance
import pandas as pd
from folium.plugins import BoatMarker

from boats import DIR_HTML, DIR_ROUTE_IN
from boats.lib.common import Boat, DEFAULT_ZOOM


def main(args):

    zoom_start = str(DEFAULT_ZOOM)

    parser = argparse.ArgumentParser(description='Displays the current boat position and the route on Folium map, '
                                                 'or saves the map as HTML.')
    parser.add_argument('boat_name')
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--route_file', type=str)
    parser.add_argument('--noview', action='store_true')
    args = parser.parse_args(args)
    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)

    fn_map = '{}.html'.format(args.boat_name)

    f_map = os.path.join(DIR_HTML, fn_map)
    f_json = os.path.join(DIR_ROUTE_IN, '{}.json'.format(args.route_file))

    df = pd.read_json(f_json)
    df.columns = ['Name', 'Points']
    df.drop('Name', axis=1, inplace=True)
    df.drop(0, axis=0, inplace=True)
    df['epoch'] = [df['Points'][idx][0] for idx in df.index]
    df['Lon'] = [float(df['Points'][idx][1]) / 1000 for idx in df.index]
    df['Lat'] = [float(df['Points'][idx][2]) / 1000 for idx in df.index]
    df.drop('Points', axis=1, inplace=True)
    df['epoch'] = df['epoch'].astype(int)
    df['ETA'] = [datetime.fromtimestamp(x).strftime("%d-%h %H:%M") for x in df['epoch']]
    df.drop('epoch', axis=1, inplace=True)

    mymap = folium.Map(location=[df.iloc[1]['Lat'], df.iloc[1]['Lon']], zoom_start=zoom_start)

    # boat
    o_boat = Boat(args.boat_name)
    o_boat.getdata()
    pos = o_boat.pos
    wind = o_boat.wind
    curr_pos = [round(pos[0], 3), round(pos[1], 3)]
    sog = o_boat.nav['sog']
    hdg = o_boat.nav['hdg']
    popup = '{},{} {}° {} kn'.format(curr_pos[0], curr_pos[1], hdg, sog)

    # TODO Add header as in track.py

    BoatMarker(curr_pos, color='blue',
               heading=hdg,
               wind_heading=wind['twd'],
               wind_speed=wind['tws'],
               popup=popup).add_to(mymap)

    # route line
    points = [(df.iloc[i]['Lat'], df.iloc[i]['Lon']) for i in range(len(df.index))]
    folium.PolyLine(points, color='red').add_to(mymap)

    # route points
    markers = [(i + 1, df.iloc[i]['Lat'], df.iloc[i]['Lon'],) for i in range(len(df.index))]

    for i in range(len(markers)):
        name = markers[i][0]
        lat = markers[i][1]
        lon = markers[i][2]
        dist = round(geopy.distance.geodesic((lat, lon), curr_pos).nm)
        popup = '{} {},{} {} nm {} hrs'.format(name, round(lat, 3), round(lon, 3), dist, round(dist / sog))
        folium.Marker([lat, lon], popup=popup).add_to(mymap)

    mymap.save(f_map)

    if not args.noview:
        webbrowser.open(f_map)


if __name__ == '__main__':
    main(sys.argv[1:])
