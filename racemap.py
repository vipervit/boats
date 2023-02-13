#!/usr/bin/env python
# coding: utf-8
import argparse
import os
import sys
import webbrowser
from datetime import datetime

import folium
import geopy.distance
import pandas as pd
from folium.plugins import BoatMarker

from boats import DIR_HTML
from boats.lib.common import timeago, get_race_data, DEFAULT_ZOOM


def make_dataframe(data):
    data = [(data[boat]['ubtname'],
             data[boat]['lat_dec'],
             data[boat]['lon_dec'],
             data[boat]['rank'],
             data[boat]['track'],
             int(data[boat]['timestamp'] / 1000),
             datetime.fromtimestamp(int(data[boat]['timestamp'] / 1000)).strftime('%d-%h-%H:%M'),
             data[boat]['heading'],
             data[boat]['lastreport_speed'],
             data[boat]['wind'].split(',')[0].strip('°'),
             data[boat]['wind'].split(',')[1].strip().strip('kn.'),
             data[boat]['resultdescr'].split(',')[3].split('nm')[0].split('.')[0].strip())
            for boat in list(data.keys()) if 'lat_dec' in data[boat]]
    df = pd.DataFrame(data, columns=['Boat', 'Lat', 'Lon', 'Rank', 'Track', 'Timestamp', 'Last', 'HDG',
                                     'SPD', 'TWD', 'TWS', 'DTW'])
    df['Rank'] = df['Rank'].astype(int)
    df = df.set_index('Rank')
    df.sort_values('Rank', ascending=True, inplace=True)
    return df.copy()


def main(args):
    parser = argparse.ArgumentParser(description='Shows the race status, with or without the map.')
    parser.add_argument('--boat_name')
    parser.add_argument('--race_name', type=str)
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--noview', action='store_true')
    args = parser.parse_args(args)

    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)
    else:
        zoom_start = str(DEFAULT_ZOOM)

    f_html = os.path.join(DIR_HTML, '{}.html'.format(args.race_name))

    df = make_dataframe(get_race_data(args.race_name))

    timestamp = df.loc[df.Boat == args.boat_name, 'Timestamp'].values[0]  # must be before the next line
    curr_pos = df[df['Boat'] == args.boat_name][['Lat', 'Lon']].values
    df['Dist'] = [round(geopy.distance.geodesic((df[['Lat', 'Lon']].values[i]), curr_pos).nm) for i in range(len(df))]
    df.at[df[df['Boat'] == args.boat_name].index[0], 'Dist'] = '...'
    df.at[df[df['Boat'] == args.boat_name].index[0], 'Boat'] = '<======= ' + args.boat_name + ' =======>'

    behind = df.iloc[0]['Dist']

    print('{}\n'.format(df[['Boat', 'SPD', 'TWS', 'DTW', 'Dist', 'Last']]))
    print('Behind leader by: {} nm'.format(round(behind), 2))

    colors = ['red', 'green', 'darkblue', 'orange', 'pink', 'darkgreen',
              'beige', 'darkred', 'purple', 'darkpurple']

    last_updated = datetime.fromtimestamp(timestamp).strftime('%d-%h-%H:%M')
    updated_ago = timeago(timestamp)
    ago_hrs = str(updated_ago[0])
    ago_mins = str(updated_ago[1])
    if len(ago_hrs) < 2:
        ago_hrs = '0' + ago_hrs
    if len(ago_mins) < 2:
        ago_mins = '0' + ago_mins

    title_html = '<h3 align="center" style="font-size:16px"><b>Last updated {} ({}:{} ago)</b></h3>'.format(
        last_updated,
        ago_hrs,
        ago_mins)

    mymap = folium.Map(location=curr_pos, zoom_start=zoom_start)
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
        if args.boat_name in df.loc[idx, 'Boat']:
            name = args.boat_name
            color = 'blue'
        popup = '{}: {} {} kn'.format(str(rank), name, spd)

        BoatMarker([lat, lon], color=color,
                   heading=hdg,
                   wind_heading=twd,
                   wind_speed=tws,
                   popup=popup).add_to(mymap)
        folium.PolyLine(track, color=color, weight=2.5, opacity=1).add_to(mymap)

    mymap.save(f_html)

    if not args.noview:
        webbrowser.open('file:{}'.format(f_html))


if __name__ == '__main__':
    main(sys.argv[1:])
