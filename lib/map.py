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
        self._boat_heel = data['heel']
        self._boat_cog = data['cog']
        self._markerdata = None
        if 'marker_data' in data.keys():
            self._markerdata = data['marker_data']
        if 'track' in data.keys():
            self._track = data['track']
        if 'route' in data.keys():
            self._route = data['route']
        self._zoom = DEFAULT_ZOOM
        self._folium = None
        self._mfile = os.path.join(DIR_MAPS, '{}.html'.format(self._boat_name))
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

        self._folium = folium.Map(location=self._loc, zoom_start=self.zoom)

        popup = '{},{} {}° (hdg) {} kn'.format(self._loc[0], self._loc[1], self.boat_marker['hdg'], self.boat_marker['sog'])
        BoatMarker(self._loc, color='blue',
                   heading=self._boat_cog,
                   wind_heading=self._markerdata['twd'],
                   wind_speed=self._markerdata['tws'],
                   popup=popup).add_to(self._folium)

        # df = get_route_from_txt_as_df(self._route)

        # # route
        # points = [(df.iloc[i]['Lat'], df.iloc[i]['Lon']) for i in range(len(df.index))]
        # folium.PolyLine(points, color='red').add_to(self._folium)
        # markers = [(df.iloc[i]['Name'], df.iloc[i]['Lat'], df.iloc[i]['Lon'],) for i in range(len(df.index))]

        # track
        # folium.PolyLine(self.track, color='green').add_to(self._folium)

        # for i in range(len(markers)):
        #     name = markers[i][0]
        #     lat = markers[i][1]
        #     lon = markers[i][2]
        #     dist = round(geopy.distance.geodesic((lat, lon), self._loc).nm)
        #     popup = '{}  {},{} {} nm {}'.format(name, round(lat, 3), round(lon, 3), dist, calculate_eta(
        #         self.boat_marker['sog'], dist))
        #     folium.Marker([lat, lon], popup=popup).add_to(self._folium)

        timestamp = datetime.datetime.now().strftime('%d-%b %H:%M')
        title_html = '<h3 align="center" style="font-size:16px">{} cog {}° sog {} tws {} heel {}<b></b></h3>'.format(
            timestamp, self._boat_cog, self.boat_marker['sog'], self._markerdata['tws'], self._boat_heel)
        self._folium.get_root().html.add_child(folium.Element(title_html))
        self._folium.save(self.mfile)

    def __get_url__(self):
        lat = self._loc[0]
        lon = self._loc[1]
        zoom = self._zoom
        name = self._boat_name
        if self.mtype is None:
            raise ValueError('Map type is not set.')
        if self.mtype == Maps.Windy:
            return 'https://www.windy.com/distance{},{}?{},{},{}'.format(lat, lon, lat, lon, zoom)
        elif self.mtype == Maps.I_Boating:
            return 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
                   '-navigation.html#{}/{}/{}'.format(zoom, lat, lon)
        elif self.mtype == Maps.Folium:
            return 'file://{}'.format(self.mfile)
        elif self.mtype == Maps.Open_Sea:
            return 'https://map.openseamap.org/?zoom={}&lon={}&lat={}&layers=TFTFFFTFFTFFFFFFTFFFTF&mlat={}' \
                   '&mlon={}&mtext={}'.format(zoom, lon, lat, lat, lon, name)
        else:
            raise ValueError('Invalid map mtype: {}'.format(self.mtype))
