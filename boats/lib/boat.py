import warnings

from boats import datasource
from boats.lib.map import Map, MapMarker
from boats.lib.nav import Nav

warnings.simplefilter(action='ignore', category=FutureWarning)


class Boat:

    def __init__(self, name, getdata=True):
        self.name = name
        self._nav = Nav(boat_name=name, getdata=getdata)
        if getdata:
            self.update_from_server()

    @property
    def nav(self):
        return self._nav

    @property
    def map(self):
        return self._map

    @property
    def log(self):
        return self.nav.log

    def update_from_log(self):
        self.nav.savetolog = False
        self.__update__(src=datasource.local)

    def update_from_server(self, savetolog=False):
        self.nav.savetolog = savetolog
        self.__update__(src=datasource.remote)

    def __update__(self, src):
        self.nav.datasource = src
        self.nav.update()
        self.__set_map__()

    def __set_map__(self):
        marker = MapMarker(location=self.nav.position,
                           heading=self.nav.az['hdg'],
                           wind_heading=self.nav.wind['twd'],
                           wind_speed=self.nav.wind['tws'])
        self._map = Map(boat_name=self.name,
                        location=self.nav.position,
                        track=self.nav.log.track,
                        marker=marker)
        self.map.set(title=self.__set_map_title__())

    def __set_map_title__(self):
        title = None
        match self.nav.datasource:
            case datasource.remote:
                title = self.nav.last_update.split(' ')
                title.pop()  # leave timestamp only
                title = ' '.join(title)
            case datasource.local:
                title = f'{self.log.last_record_timestamp_local} (log)'
        return title

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return 0
