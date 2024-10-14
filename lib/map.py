import datetime
import os
import webbrowser

import folium
import pandas as pd
from folium.plugins import BoatMarker

from boats import DIR_MAPS, DIR_SAILDATA
from boats.lib.common import DEFAULT_ZOOM, DEFAULT_MAP, Maps


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
        if 'sailplan' in data.keys():
            self._boat_sailplan=data['sailplan']
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
        folium.PolyLine(self.track, color='red', weight=2.5, opacity=1).add_to(self._folium)

        popup = self.__get_url_i_boating__()

        BoatMarker(self._loc, color='blue',
                   heading=self._boat_cog,
                   wind_heading=self._markerdata['twd'],
                   wind_speed=self._markerdata['tws'],
                   popup=popup).add_to(self._folium)

        timestamp = datetime.datetime.now().strftime('%d-%b %H:%M')
        title_html = '<h3 align="center" style="font-size:16px">{} cog {}° sog {} tws {} heel {} sails: {}<b></b></h3>'.format(
            timestamp, self._boat_cog, self.boat_marker['sog'], self._markerdata['tws'], self._boat_heel, self._boat_sailplan)
        self._folium.get_root().html.add_child(folium.Element(title_html))

        self._folium.save(self.mfile)

    def __get_url_i_boating__(self):
        return 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
               '-navigation.html#{}/{}/{}'.format(self._zoom, self._loc[0], self._loc[1])

    def __get_url__(self):
        lat = self._loc[0]
        lon = self._loc[1]
        zoom = self._zoom
        name = self._boat_name
        if self.mtype is None:
            raise ValueError('Map type is not set.')
        if self.mtype == Maps.Windy:
            return 'https://www.windy.com/?{},{},{},m:eT5aeSC'.format(lat, lon, zoom)
        elif self.mtype == Maps.I_Boating:
            return self.__get_url_i_boating__()
        elif self.mtype == Maps.Folium:
            return 'file://{}'.format(self.mfile)
        elif self.mtype == Maps.Open_Sea:
            return 'https://map.openseamap.org/?zoom={}&lon={}&lat={}&layers=TFTFFFTFFTFFFFFFTFFFTF&mlat={}' \
                   '&mlon={}&mtext={}'.format(zoom, lon, lat, lat, lon, name)
        else:
            raise ValueError('Invalid map mtype: {}'.format(self.mtype))
