import json
import os
import time

import pandas as pd
import warnings
from io import StringIO

from boats import DIR_SAILDATA, POINTS_OF_SAIL
from boats.lib.common import get_all_own_boats_json, dd_to_ddm
from boats.lib.map import Map

warnings.simplefilter(action='ignore', category=FutureWarning)

class Boat:

    def __init__(self, name):
        self._map = Map(boat_name=name)
        self.nav = None
        self.wind = None
        self.heel = None
        self.pos = None
        self.sailplan = None
        self.sails = None
        self.name = name
        self.data = None
        self.datafile = os.path.join(DIR_SAILDATA, name + '_dat.json')
        self._track = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return 0

    def get_data(self, response_json=False, save=True):
        if not response_json:
            response_json = get_all_own_boats_json()
        for data in response_json:
            if data['boatname'] == self.name:
                self.data = data
        self.sails = [sail['sail'] for sail in self.data['sails']]
        self.sailplan = [sail['sail'] for sail in self.data['sails'] if sail['halyard'] == 1 and sail['furled'] == 0]
        self.pos = (round(self.data['latitude'], 5), round(self.data['longitude'], 5))
        self.heel = abs(round(self.data['heeldegrees'], ))
        self.wind = {'tws': round(self.data['tws'] * 2, 1),
                     'twa': round(self.data['twa']),
                     'twd': round(self.data['twd']),
                     'aws': round(self.data['aws'] * 2),
                     'awa': round(self.data['awa'])}
        self.nav = {'hdg': round(self.data['hdg']),
                    'spd': round(self.data['spd'] * 2, 1),
                    'cog': round(self.data['cog']),
                    'sog': round(self.data['sog'] * 2, 1),
                    'whl': round(self.data['weatherhelm'], 2)
                    }
        if save:
            self.save_current_sail_data()
        self._map = Map(
            boat_name=self.name,
            location=self.pos,
            heel=self.heel,
            cog=self.nav['cog'],
            track=self.__get_track_from_log__(),
            sailplan=self.sailplan,
            marker_data={
                'heel': self.heel,
                'sog': self.nav['sog'],
                'hdg': self.nav['hdg'],
                'twd': self.wind['twd'],
                'tws': self.wind['tws']}
        )
        self._map.track = self._track
        return self.data

    def show_pos(self):
        print('{}, {}'.format(self.pos[0], self.pos[1]))
        print(dd_to_ddm((self.pos[0], self.pos[1])))
        print('\n')

    def show_sailplan(self):
        for sail in self.sails:
            mark = ''
            if sail in self.sailplan:
                mark = 'X'
            print(sail.lower() + ':' + ' ' * (16 - len(sail)) + mark)

    def show_point_of_sail(self):
        print(f'on {self.__get_point_of_sail__()}\n')

    def show_heel(self):
        print('heel: {}'.format(abs(self.heel)))
        print('\n')

    def show_speed(self):
        print('tws : {}'.format(self.wind['tws']))
        print('spd : {}'.format(self.nav['spd']))
        print('sog : {}'.format(self.nav['sog']))
        print('\n')

    def show_course(self):
        print('hdg : {}'.format(self.nav['hdg']))
        print('cog : {}'.format(self.nav['cog']))
        print('\n')

    def show(self, full=False):
        print('\n{}\n'.format(self.name.upper()))
        if full:
            self.__show_full__()
        else:
            self.__show_short__()

    def show_efficiency(self):
        print('Efficiency: {}%'.format(round(self.nav['spd'] / self.wind['tws'], 2) * 100))

    def sail_config_snapshot(self):
        return {'tws': self.wind['tws'],
                'spd': self.nav['spd'],
                'twd': self.wind['twd'],
                'twa': self.wind['twa'],
                'awa': self.wind['awa'],
                'heel': self.heel,
                'lat': self.pos[0],
                'lon': self.pos[1],
                'sails': self.sailplan}

    def save_current_sail_data(self):
        data = {}
        if os.path.exists(self.datafile):
            data = self.__read_sail_data_from_file__()
        data.update({str(time.time()): self.sail_config_snapshot()})
        self.__write_sail_data_to_file__(data)

    def get_track(self):
        return self._track

    def get_logged_data(self):
        return pd.read_json(StringIO(json.dumps(self.__read_sail_data_from_file__())), orient='index')

    def __get_track_from_log__(self):
        df = self.get_logged_data()
        df.sort_index(ascending=False, inplace=True)
        df_track = df[['lat', 'lon']].dropna()
        self._track = [[df_track.loc[i, 'lat'], df_track.loc[i, 'lon']] for i in df_track.index]

    # ------------
    @property
    def map(self):
        return self._map

    def __show_short__(self):
        self.show_pos()
        print('tws: {}'.format(self.wind['tws']))
        print('sog: {}'.format(self.nav['sog']))
        print('twd: {}'.format(self.wind['twd']))
        print('hdg: {}'.format(self.nav['hdg']))
        print('heel {}'.format(self.heel))
        print('\n')
        self.show_point_of_sail()

    def __show_full__(self):
        self.show_pos()
        self.show_sailplan()
        self.show_point_of_sail()
        for each in self.nav:
            print('{}: {}'.format(each, abs(self.nav[each])))
        for each in self.wind:
            print('{}: {}'.format(each, abs(self.wind[each])))
        print('\n')
        self.show_heel()
        self.show_efficiency()

    def __read_sail_data_from_file__(self):
        with open(self.datafile, 'r') as f:
            return json.load(f)

    def __write_sail_data_to_file__(self, dic):
        with open(self.datafile, 'w') as f:
            json.dump(dic, f)

    def __get_point_of_sail__(self):
        for p_of_sail in POINTS_OF_SAIL:
            if abs(self.wind['twa']) in POINTS_OF_SAIL[p_of_sail]:
                return p_of_sail

    @map.setter
    def map(self, value):
        self._map = value
