import warnings

from boats import datasource, DEFAULT_ZOOM
from boats.lib.log import Log
from boats.lib.map import Map, MapMarker
from boats.lib.nav import Nav

warnings.simplefilter(action='ignore', category=FutureWarning)


# TODO: Ensure accounting for both 1) no log file existing and/or 2) no html file existing.
class Boat:

    def __init__(self, name, getdata=True, savetolog=False):
        self.name = name
        self._savetolog = savetolog
        self._nav = Nav(self)
        self._log = Log(self.name)
        self._map = None
        self._last_update = None
        self.map_zoom = DEFAULT_ZOOM
        if getdata:
            self.update_from_server()

    @property
    def nav(self):
        return self._nav

    @property
    def map(self):
        return self._map

    @property
    def savetolog(self):
        return self._savetolog

    @savetolog.setter
    def savetolog(self, val):
        self._savetolog = val

    @property
    def log(self):
        return self._log

    @property
    def last_update(self):
        return self._last_update

    @last_update.setter
    def last_update(self, val):
        self._last_update = val

    def update_from_log(self):
        self.nav.datasource = datasource.local
        self.nav.get_data()

    def update_from_server(self):
        self.nav.datasource = datasource.remote
        self.nav.get_data()
        if self.savetolog:
            self.__make_log_entry__()
            self.log.load()
        self.__set_map__()

    def __set_map__(self):
        ts, saveindicator = None, None
        wpt = self.nav.wpt
        marker = MapMarker(location=self.nav.position,
                           heading=self.nav.az['hdg'],
                           wind_heading=self.nav.wind['twd'],
                           wind_speed=self.nav.wind['tws'])
        self._map = Map(boat_name=self.name,
                        location=self.nav.position,
                        track=self.log.track,
                        marker=marker,
                        zoom_start=self.map_zoom)
        if wpt is not None:
            self._map.course_line = [self.nav.position, wpt]
        match self.nav.datasource:
            case datasource.remote:
                saveindicator = ''
            case datasource.local:
                saveindicator = '*'
        self.map.set(title=f'{self.name} {self.last_update}{saveindicator}')

    def __make_log_entry__(self):
        self.log.add_new(self.nav.collect_data_for_saving_in_log__())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return 0
