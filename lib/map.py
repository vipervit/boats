import datetime
import os
import webbrowser

import folium
from folium.plugins import BoatMarker

from boats import DIR_MAPS, DEFAULT_ZOOM, URL_OPENSEA, URL_WINDY, URL_IBOATING
from boats import DEFAULT_MAP, Maps

DEFAULT_LOCATION = [0.00, 0.00]


class MapMarker:
    def __init__(self, **kwargs):
        if 'location' in kwargs.keys():
            self._loc = kwargs['location']
        if 'heading' in kwargs.keys():
            self._hdg = kwargs['heading']
        if 'wind_heading' in kwargs.keys():
            self._windhdg = kwargs['wind_heading']
        if 'wind_speed' in kwargs.keys():
            self._windspd = kwargs['wind_speed']
        if 'popup' in kwargs.keys():
            self._p = kwargs['popup']

    @property
    def location(self):
        return self._loc

    @property
    def heading(self):
        return self._hdg

    @property
    def wind_heading(self):
        return self._windhdg

    @property
    def wind_speed(self):
        return self._windspd

    @property
    def popup(self):
        return self._p


class Map:

    def __init__(self, boat_name, **kwargs):
        self.boat_name = boat_name
        self._data = None
        self._marker = None
        self._map_folium = None
        self._url = None
        self._track = None
        self._title = datetime.datetime.now().strftime('%d-%b %H:%M')
        self._loc = DEFAULT_LOCATION
        self._zoom = DEFAULT_ZOOM
        self._mtype = DEFAULT_MAP
        self._mfile = os.path.join(DIR_MAPS, '{}.html'.format(self.boat_name))
        self.set(**kwargs)

    @property
    def title(self):
        return self._title

    @property
    def mtype(self):
        return self._mtype

    @mtype.setter
    def mtype(self, val):
        self._mtype = val

    @property
    def mfile(self):
        return self._mfile

    def set(self, **kwargs):
        if 'type' in kwargs.keys():
            self.mtype = kwargs['type']
        if 'location' in kwargs.keys():
            self._loc = kwargs['location']
        if 'marker' in kwargs.keys():
            if self._mtype != Maps.Folium:
                raise ValueError('Can only use boat marker with Folium!')
            self._marker = kwargs['marker']
        if 'track' in kwargs.keys():
            self._track = kwargs['track']
        if 'title' in kwargs.keys():
            self._title = kwargs['title']
        if 'zoom_start' in kwargs.keys():
            self._zoom = kwargs['zoom_start']
        if self.mtype == Maps.Folium:
            self.__save_folium_html__()

    def show(self, timestamp=None):
        webbrowser.open(self.__get_url__())

    def __save_folium_html__(self):
        self.__prepare_folium__()
        self._map_folium.save(self._mfile)

    def __delete_folium_html__(self):
        os.remove(self._mfile)

    def __prepare_folium__(self):
        self._map_folium = folium.Map(location=self._loc, zoom_start=self._zoom)
        folium.TileLayer('openseamap').add_to(self._map_folium)
        if self._track is not None:
            folium.PolyLine(self._track, color='red', weight=2.5, opacity=1).add_to(self._map_folium)

        popup = self.__get_url_i_boating__()

        if self._marker is None:
            raise ValueError('Boat marker is note set.')

        BoatMarker(location=self._marker.location, color='blue',
                   heading=self._marker.heading,
                   wind_heading=self._marker.wind_heading,
                   wind_speed=self._marker.wind_speed,
                   popup=popup).add_to(self._map_folium)
        title_html = f'<h3 align="center" style="font-size:16px">{self._title}<b></b></h3>'
        self._map_folium.get_root().html.add_child(folium.Element(title_html))

    def __get_url_i_boating__(self):
        return URL_IBOATING.format(self._zoom, self._loc[0], self._loc[1])

    def __get_url_folium__(self):
        return 'file://{}'.format(self._mfile)

    def __get_url_opensea__(self):
        return URL_OPENSEA.format(self._zoom, self._loc[1], self._loc[0], self._loc[0], self._loc[1], self.boat_name)

    def __get_url_windy__(self):
        return URL_WINDY.format(self._loc[0], self._loc[1], self._zoom)

    def __get_url__(self):
        match self._mtype:
            case Maps.Folium:
                return self.__get_url_folium__()
            case Maps.I_Boating:
                return self.__get_url_i_boating__()
            case Maps.Windy:
                return self.__get_url_windy__()
            case Maps.Open_Sea:
                return self.__get_url_opensea__()
            case None:
                raise ValueError('Map type is not set.')
            case _:
                raise ValueError('Invalid map mtype: {}'.format(self._mtype))
