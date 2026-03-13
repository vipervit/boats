import datetime
import os
import sys
import webbrowser

import folium
from folium.plugins import BoatMarker

from boats import DEFAULT_MAP, Maps
from boats import DIR_MAPS, DEFAULT_ZOOM, URL_OPENSEA, URL_WINDY, URL_IBOATING

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
        self._courseline = None
        self._target_line = None
        self._target_point = None
        self._target_course = None
        self._target_pick_enabled = False
        self.boat_name = boat_name
        self._data = None
        self._marker = None
        self._map_folium = None
        self._url = None
        self._track = None
        self._title = datetime.datetime.now().strftime('%d-%b %H:%M')
        self._loc = DEFAULT_LOCATION
        self._view_center = DEFAULT_LOCATION
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

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, val):
        self._zoom = val

    @property
    def course_line(self):
        return self._courseline

    @course_line.setter
    def course_line(self, val):
        self._courseline = val

    @property
    def target_line(self):
        return self._target_line

    @target_line.setter
    def target_line(self, val):
        self._target_line = val

    @property
    def target_point(self):
        return self._target_point

    @target_point.setter
    def target_point(self, val):
        self._target_point = val

    @property
    def target_course(self):
        return self._target_course

    @target_course.setter
    def target_course(self, val):
        self._target_course = val

    @property
    def target_pick_enabled(self):
        return self._target_pick_enabled

    @target_pick_enabled.setter
    def target_pick_enabled(self, val):
        self._target_pick_enabled = bool(val)

    def set(self, **kwargs):
        if 'type' in kwargs.keys():
            self.mtype = kwargs['type']
        if 'location' in kwargs.keys():
            self._loc = kwargs['location']
            if self._view_center == DEFAULT_LOCATION:
                self._view_center = kwargs['location']
        if 'view_center' in kwargs.keys():
            self._view_center = kwargs['view_center']
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
        if 'course_line' in kwargs.keys():
            self._courseline = kwargs['course_line']
        if 'target_line' in kwargs.keys():
            self._target_line = kwargs['target_line']
        if 'target_point' in kwargs.keys():
            self._target_point = kwargs['target_point']
        if 'target_course' in kwargs.keys():
            self._target_course = kwargs['target_course']
        if 'target_pick_enabled' in kwargs.keys():
            self._target_pick_enabled = bool(kwargs['target_pick_enabled'])
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
        self._map_folium = folium.Map(location=self._view_center, zoom_start=self._zoom)
        if sys.platform == 'darwin':  # temporary workaround for Windows
            folium.TileLayer('openseamap').add_to(self._map_folium)
        if self._track is not None:
            folium.PolyLine(self._track, color='red', weight=2.5, opacity=1).add_to(self._map_folium)
        if self._courseline is not None:
            folium.PolyLine(locations=self._courseline, color='blue', weight=0.5, opacity=0.5).add_to(self._map_folium)
        if self._target_line is not None:
            target_line = folium.PolyLine(
                locations=self._target_line,
                color='#ffb14a',
                weight=2,
                opacity=0.8,
                dash_array='6, 8'
            )
            target_line.add_to(self._map_folium)
        if self._target_point is not None:
            target_marker = folium.Marker(
                location=self._target_point,
                draggable=True,
                popup='Picked point',
                icon=folium.DivIcon(
                    html=(
                        '<div style="'
                        'width: 14px; '
                        'height: 14px; '
                        'border-radius: 50%; '
                        'background: #ffb14a; '
                        'border: 2px solid #fff3c6; '
                        'box-shadow: 0 0 0 2px rgba(7, 20, 28, 0.42);'
                        '"></div>'
                    )
                )
            )
            if self._target_course is not None:
                folium.Tooltip(
                    f'{self._target_course} deg',
                    permanent=True,
                    direction='top',
                    offset=(0, -8),
                    style=(
                        'background-color: rgba(7, 20, 28, 0.92); '
                        'border: 1px solid #ffb14a; '
                        'border-radius: 4px; '
                        'box-shadow: none; '
                        'color: #ffefc2; '
                        'font-size: 12px; '
                        'font-weight: 600; '
                        'padding: 2px 6px;'
                    )
                ).add_to(target_marker)
            target_marker.add_to(self._map_folium)

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
        self._map_folium.get_root().script.add_child(folium.Element(
            f"""
            (function attachMapClickHandler() {{
                var mapInstance = window["{self._map_folium.get_name()}"];
                if (!mapInstance) {{
                    window.setTimeout(attachMapClickHandler, 50);
                    return;
                }}
                window.boatsMapInstance = mapInstance;
                window.boatsTargetPickEnabled = {str(self._target_pick_enabled).lower()};

                function publishViewState(prefix) {{
                    var center = mapInstance.getCenter();
                    document.title = prefix +
                        mapInstance.getZoom() + ',' +
                        center.lat.toFixed(5) + ',' +
                        center.lng.toFixed(5);
                }}

                mapInstance.on('click', function(e) {{
                    if (!window.boatsTargetPickEnabled) {{
                        return;
                    }}
                    var center = mapInstance.getCenter();
                    document.title = 'map-click:' +
                        e.latlng.lat.toFixed(5) + ',' +
                        e.latlng.lng.toFixed(5) + ',' +
                        mapInstance.getZoom() + ',' +
                        center.lat.toFixed(5) + ',' +
                        center.lng.toFixed(5);
                }});
                mapInstance.on('moveend', function() {{
                    publishViewState('map-view-state:');
                }});
                mapInstance.on('zoomend', function() {{
                    if (window.boatsTargetPickEnabled) {{
                        var center = mapInstance.getCenter();
                        document.title = 'map-pick-cancel:' +
                            mapInstance.getZoom() + ',' +
                            center.lat.toFixed(5) + ',' +
                            center.lng.toFixed(5);
                    }}
                }});
                window.setTimeout(function() {{
                    publishViewState('map-view-state:');
                }}, 0);
            }})();
            """
        ))
        if self._target_point is not None and self._target_line is not None:
            self._map_folium.get_root().script.add_child(folium.Element(
                f"""
                (function attachTargetDragHandler() {{
                    var targetMarker = window["{target_marker.get_name()}"];
                    var targetLine = window["{target_line.get_name()}"];
                    if (!targetMarker || !targetLine) {{
                        window.setTimeout(attachTargetDragHandler, 50);
                        return;
                    }}

                    function calculateCourse(lat1, lon1, lat2, lon2) {{
                        var radians = Math.PI / 180.0;
                        var degrees = 180.0 / Math.PI;
                        var phi1 = lat1 * radians;
                        var phi2 = lat2 * radians;
                        var deltaLambda = (lon2 - lon1) * radians;
                        var y = Math.sin(deltaLambda) * Math.cos(phi2);
                        var x = Math.cos(phi1) * Math.sin(phi2) -
                            Math.sin(phi1) * Math.cos(phi2) * Math.cos(deltaLambda);
                        var bearing = Math.atan2(y, x) * degrees;
                        return Math.round((bearing + 360) % 360);
                    }}

                    function updateTargetOverlay(latlng) {{
                        var course = calculateCourse({self._loc[0]}, {self._loc[1]}, latlng.lat, latlng.lng);
                        targetLine.setLatLngs([[{self._loc[0]}, {self._loc[1]}], [latlng.lat, latlng.lng]]);
                        if (targetMarker.getTooltip()) {{
                            targetMarker.setTooltipContent(course + ' deg');
                        }}
                    }}

                    targetMarker.on('drag', function(e) {{
                        updateTargetOverlay(e.target.getLatLng());
                    }});

                    targetMarker.on('dragend', function(e) {{
                        var latlng = e.target.getLatLng();
                        var center = targetMarker._map.getCenter();
                        updateTargetOverlay(latlng);
                        window.setTimeout(function() {{
                            targetMarker._boatsSuppressClear = false;
                        }}, 150);
                        document.title = 'map-click:' +
                            latlng.lat.toFixed(5) + ',' +
                            latlng.lng.toFixed(5) + ',' +
                            targetMarker._map.getZoom() + ',' +
                            center.lat.toFixed(5) + ',' +
                            center.lng.toFixed(5);
                    }});

                    targetMarker.on('dragstart', function() {{
                        targetMarker._boatsSuppressClear = true;
                    }});

                    targetMarker.on('click', function() {{
                        if (targetMarker._boatsSuppressClear) {{
                            return;
                        }}
                        document.title = 'map-target-clear';
                    }});
                }})();
                """
            ))

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
