import datetime
import os
import webbrowser

import folium
import geopy.distance
from folium.plugins import BoatMarker

from boats import DIR_MAPS
from lib.common import DEFAULT_ZOOM, DEFAULT_MAP, calculate_eta, Maps
from lib.df_route import get_route_from_txt_as_df


class Map:

    def __init__(self, **data):

        self._boat_name = data['boat_name']
        self._loc = data['location']
        self._track = None
        self._route = self._boat_name
        self._markerdata = None
        if 'marker_data' in data.keys():
            self._markerdata = data['marker_data']
        if 'track' in data.keys():
            self._track = data['track']
        if 'route' in data.keys():
            self._route = data['route']
        self._folium = folium.Map(location=self._loc)
        self._mfile = os.path.join(DIR_MAPS, '{}.html'.format(self._boat_name))
        self._zoom = DEFAULT_ZOOM
        self._url = None
        self._mtype = DEFAULT_MAP

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        self._url = val

    @property
    def mtype(self):
        return self._mtype

    @mtype.setter
    def mtype(self, val):
        if val is not None:
            self._mtype = val

    @property
    def mfile(self):
        return self._mfile

    @mfile.setter
    def mfile(self, val):
        self._mfile = val

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, val):
        self._zoom = val

    @property
    def track(self):
        return self._track

    @track.setter
    def track(self, val):
        self._track = val

    @property
    def route_name(self):
        return self._route

    @route_name.setter
    def route_name(self, val):
        self._route = val

    @property
    def boat_marker(self):
        return self._markerdata

    @boat_marker.setter
    def boat_marker(self, val):
        self._markerdata = val
        if self.mtype == Maps.Folium:
            self.__prepare_folium__()

    def show(self):
        if self.mtype == Maps.Folium:
            self.__prepare_folium__()
        webbrowser.open(self.__get_url__())

    def __prepare_folium__(self):

        popup = '{},{} {} dg {} kn'.format(self._loc[0], self._loc[1], self.boat_marker['hdg'], self.boat_marker['sog'])
        track = self.track
        BoatMarker(self._loc, color='blue',
                   heading=self._markerdata['hdg'],
                   wind_heading=self._markerdata['twd'],
                   wind_speed=self._markerdata['tws'],
                   popup=popup).add_to(self._folium)

        df = get_route_from_txt_as_df(self._route)

        # route
        points = [(df.iloc[i]['Lat'], df.iloc[i]['Lon']) for i in range(len(df.index))]
        folium.PolyLine(points, color='red').add_to(self._folium)
        markers = [(df.iloc[i]['Name'], df.iloc[i]['Lat'], df.iloc[i]['Lon'],) for i in range(len(df.index))]

        # track
        folium.PolyLine(track, color='green').add_to(self._folium)

        for i in range(len(markers)):
            name = markers[i][0]
            lat = markers[i][1]
            lon = markers[i][2]
            dist = round(geopy.distance.geodesic((lat, lon), self._loc).nm)
            popup = '{}  {},{} {} nm {}'.format(name, round(lat, 3), round(lon, 3), dist, calculate_eta(
                self.boat_marker['sog'], dist))
            folium.Marker([lat, lon], popup=popup).add_to(self._folium)

        timestamp = datetime.datetime.now().strftime('%d %b %H:%M')
        title_html = '<h3 align="center" style="font-size:16px">{} {} dg {} kn<b></b></h3>'.format(
            timestamp, self.boat_marker['hdg'], self.boat_marker['sog'])
        self._folium.get_root().html.add_child(folium.Element(title_html))
        self._folium.save(self.mfile)

    def __get_url__(self):
        if self.mtype is None:
            raise ValueError('Map type is not set.')
        if self.mtype == Maps.Windy:
            return 'https://www.windy.com/distance{},{}?{},{},{}'.format(self._loc[0], self._loc[1], self._loc[0],
                                                                         self._loc[1], self._zoom)
        elif self.mtype == Maps.I_Boating:
            return 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
                   '-navigation.html#{}/{}/{}'.format(self._zoom, self._loc[0], self._loc[1])
        elif self.mtype == Maps.Folium:
            return 'file://{}'.format(self.mfile)
        else:
            raise ValueError('Invalid map mtype: {}'.format(self.mtype))
