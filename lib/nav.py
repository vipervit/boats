from boats import datasource, POINTS_OF_SAIL, SAILS
from boats.lib.common import get_all_own_boats_json, dd_to_ddm
from boats.lib.log import Log


class Nav:

    def __init__(self, boat_name=None, src=datasource.remote, getdata=True):
        # TODO: add ability to view time of latest update from server
        self._savetolog = False
        self._datasrc = src
        self.boatname = boat_name
        self._data = {}
        self._log = Log(boat_name=self.boatname)
        self.az = None
        if getdata:
            self.update()

    @property
    def all(self):
        return self._data

    @property
    def log(self):
        return self._log

    @property
    def datasource(self):
        return self._datasrc

    @datasource.setter
    def datasource(self, val):
        self._datasrc = val

    @property
    def savetolog(self):
        return self._savetolog

    @savetolog.setter
    def savetolog(self, val):
        self._savetolog = val

    def show(self, full=False):
        print('\n{}\n'.format(self.boatname.upper()))
        if full:
            self.__show_full__()
        else:
            self.__show_short__()

    def update(self):
        self.__check_savetolog_when_local__()
        self.__getdata__()
        if (self.datasource == datasource.remote) and (self.savetolog == True):
            # raise NotImplementedError
            # # TODO Implement saving to log (make proper data snapshot)
            self.__make_log_entry__()

    def __getdata__(self):
        match self.datasource:
            case datasource.remote:
                self.__retrieve_online_boat_data__()
            case datasource.local:
                self.__retrieve_boat_data_from_log__()
            case _:
                raise ValueError(f'Invalid value for data source: {self.datasource}.')
        self.wind = self.__get_wind__()
        self.speed = self.__get_speed__()
        self.az = self.__get_azimuths__()
        self.pos = self.__get_point_of_sail__()
        self.position = self.__get_position__()
        self.sailplan = self.__get_sailplan__()
        self.heel = self.__get_heel__()

    def __retrieve_boat_data_from_log__(self):
        self._data = self.log.last_record

    def __retrieve_online_boat_data__(self):
        response_json = get_all_own_boats_json()
        if self.boatname not in str(response_json):
            raise ValueError(f'Boat does not exist in Sailaway: \'{self.boatname}\'!')
        for data in response_json:
            if data['boatname'] == self.boatname:
                self._data = data

    def __check_savetolog_when_local__(self):
        if (self.datasource == datasource.local) and (self.savetolog == True):
            raise ValueError('Can only save in log if updated from remote.')

    def __make_log_entry__(self):
        self.log.add_new(self.__collect_log_data__())

    def __collect_log_data__(self):
        return {
            'hdg': self.az['hdg'],
            'tws': self.wind['tws'],
            'spd': self.speed['spd'],
            'twd': self.wind['twd'],
            'twa': self.wind['twa'],
            'awa': self.wind['awa'],
            'heel': self.heel,
            'lat': self.position[0],
            'lon': self.position[1],
            'sails': self.sailplan
        }

    def __show_pos__(self):
        print('{}, {}'.format(self.position[0], self.position[1]))
        print(dd_to_ddm((self.position[0], self.position[1])))
        print('\n')

    def __show_sailplan__(self):
        for sail in SAILS:
            mark = ''
            if sail in self.sailplan:
                mark = 'X'
            print(sail.lower() + ':' + ' ' * (16 - len(sail)) + mark)
        print('\n')

    def __show_point_of_sail__(self):
        print(f'on {self.__get_point_of_sail__()}\n')

    def __show_heel__(self):
        print('heel: {}'.format(abs(self.heel)))
        print('\n')

    def __show_speed__(self):
        for k, v in self.speed.items():
            print(f'{k}: {v}')
        print('\n')

    def __show_wind__(self):
        for k, v in self.wind.items():
            print(f'{k}: {v}')
        print('\n')

    def __show_course__(self):
        print('hdg : {}'.format(self.azimuth['hdg']))
        print('cog : {}'.format(self.azimuth['cog']))
        print('\n')

    def __show_efficiency__(self):
        print('Efficiency: {}%'.format(round(self.speed['spd'] / self.wind['tws'], 2) * 100))

    def __get_heel__(self):
        word = None
        match self.datasource:
            case datasource.local:
                word = 'heel'
            case datasource.remote:
                word = 'heeldegrees'
        return abs(round(self._data[word], ))

    def __get_azimuths__(self):
        d = {'hdg': round(self._data['hdg'])}
        if self.datasource == datasource.remote:
            d.update({'cog': round(self._data['cog'], )})
        return d

    def __get_speed__(self):
        d = {'spd': round(self._data['spd'] * 2, 1)}
        if self.datasource == datasource.remote:
            d.update({'cog': round(self._data['cog'] * 2, 1)})
            d.update({'sog': round(self._data['sog'] * 2, 1)})
        return d

    def __get_wind__(self):
        d = {'tws': round(self._data['tws'] * 2, 1),
             'twa': abs(round(self._data['twa'])),
             'twd': round(self._data['twd'])}
        if self.datasource == datasource.remote:
            d.update({'awa': abs(round(self._data['awa']))})
            d.update({'aws': abs(round(self._data['awa'] * 2))})
        return d

    def __get_sailplan__(self):
        match self.datasource:
            case datasource.local:
                return [sail for sail in self._data['sails']]
            case datasource.remote:
                return [sail['sail'] for sail in self._data['sails']
                        if sail['halyard'] == 1 and sail['furled'] == 0]

    def __get_position__(self):
        lat, lon = None, None
        match self.datasource:
            case datasource.local:
                lat, lon = 'lat', 'lon'
            case datasource.remote:
                lat, lon = 'latitude', 'longitude'
        return round(self._data[lat], 5), round(self._data[lon], 5)

    def __get_point_of_sail__(self):
        for p_of_sail in POINTS_OF_SAIL:
            if abs(self.wind['twa']) in POINTS_OF_SAIL[p_of_sail]:
                return p_of_sail

    def __show_short__(self):
        self.__show_pos__()
        print('\n')
        self.__show_point_of_sail__()

    def __show_full__(self):
        self.__show_pos__()
        self.__show_sailplan__()
        self.__show_point_of_sail__()
        self.__show_speed__()
        self.__show_wind__()
        self.__show_heel__()
        self.__show_efficiency__()
