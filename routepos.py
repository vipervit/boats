import argparse
import datetime
import os
import os.path
import sys
import webbrowser
from os import path

import folium
import geopy.distance
from folium.plugins import BoatMarker

from boats import DIR_HTML, DIR_ROUTE_OUT
from boats.lib.boat import Boat
from boats.lib.common import DEFAULT_ZOOM
from boats.lib.df_route import get_route_from_txt_as_df


def main(args):
    zoom_start = str(DEFAULT_ZOOM)

    parser = argparse.ArgumentParser(description='Displays the current boat position and the route on Folium map, '
                                                 'or saves the map as HTML.')
    parser.add_argument('--boat_name')
    parser.add_argument('--zoom_start', type=int)
    parser.add_argument('--route_name', type=str)
    parser.add_argument('--noview', action='store_true')

    args = parser.parse_args(args)

    if args.zoom_start is not None:
        zoom_start = str(args.zoom_start)

    # boat
    with Boat(args.boat_name) as o_boat:
        o_boat.getdata()
        pos = o_boat.pos
        wind = o_boat.wind
        curr_pos = [round(pos[0], 3), round(pos[1], 3)]
        sog = o_boat.nav['sog']
        hdg = o_boat.nav['hdg']
        popup = '{},{} {}° {} kn'.format(curr_pos[0], curr_pos[1], hdg, sog)
        track = o_boat.get_track_from_log()

    mymap = folium.Map(location=[curr_pos[0], curr_pos[1]], zoom_start=zoom_start)

    BoatMarker(curr_pos, color='blue',
               heading=hdg,
               wind_heading=wind['twd'],
               wind_speed=wind['tws'],
               popup=popup).add_to(mymap)

    if path.exists(os.path.join(DIR_ROUTE_OUT, '{}.txt'.format(args.route_name))):

        df = get_route_from_txt_as_df(args.route_name)

        # route line
        points = [(df.iloc[i]['Lat'], df.iloc[i]['Lon']) for i in range(len(df.index))]
        folium.PolyLine(points, color='red').add_to(mymap)
        folium.PolyLine(track, color='green').add_to(mymap)

        # route points
        markers = [(df.iloc[i]['Name'], df.iloc[i]['Lat'], df.iloc[i]['Lon'],) for i in range(len(df.index))]

        for i in range(len(markers)):
            name = markers[i][0]
            lat = markers[i][1]
            lon = markers[i][2]
            dist = round(geopy.distance.geodesic((lat, lon), curr_pos).nm)
            if sog != 0:
                t = dist / sog
                if t < 24:
                    days = 0
                else:
                    days = round(round(t) / 24)
                hours = round(dist / sog) - days * 24
                point_eta = '{}d {}h'.format(days, hours)
            else:
                point_eta = ''
            popup = '{}  {},{} {} nm {}'.format(name, round(lat, 3), round(lon, 3), dist, point_eta)
            folium.Marker([lat, lon], popup=popup).add_to(mymap)
    else:
        print('No route {} found.'.format(args.route_name))

    timestamp = datetime.datetime.now().strftime('%d %b %H:%M')
    title_html = '<h3 align="center" style="font-size:16px">{} {}° {} kn<b></b></h3>'.format(timestamp, hdg, sog)
    mymap.get_root().html.add_child(folium.Element(title_html))

    f_map = os.path.join(DIR_HTML, '{}.html'.format(args.boat_name))

    mymap.save(f_map)


    if not args.noview:
        webbrowser.open('file://{}'.format(f_map))

if __name__ == '__main__':
    main(sys.argv[1:])
