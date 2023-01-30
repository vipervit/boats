from datetime import datetime
import os
import requests
import pandas as pd
import json
import time

from boats import DIR_SAILDATA

MY_USER = 'Viper Vit'

API_KEY = '7B79EE2988A44080A37C06570F4B5EE8'
API_USER = '59528'

URL_RACES = 'https://sarl.ingenium.net.au/racelog?racenr='

RACE_IDS = {
    'Stardust': 38602,
    'The Ocean Race': 39147
}

API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr={}&key={}'.format(API_USER, API_KEY)
API_RACE_MARKS = 'https://backend.sailaway.world/cgi-bin/sailaway/GetMissionCourse.pl?usrnr={}&key={}&misnr=RACEID'. \
    format(API_USER, API_KEY)

URL_IBOATING_CHART = 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
                     '-navigation.html'

DEFAULT_ZOOM = 7

def get_all_own_boats_json():
    return requests.get(API_OWN_BOATS).json()


def get_race_data(race_name):
    return requests.get(get_race_api_url(race_name)).json()['result']


def get_boat_race_data(race, user, boat):
    return get_race_data(race)[user + '-' + boat]


def get_race_api_url(race_name):
    return '{}{}'.format(URL_RACES, str(RACE_IDS[race_name]))


def timestamp():
    return datetime.now().strftime('%d/%m %H:%M')


def timeago(time_stamp):
    now = datetime.fromtimestamp(datetime.now().timestamp())
    delta = (now - datetime.fromtimestamp(time_stamp)).seconds
    hrs = int(delta / 3600)
    mins = int(delta / 60) - hrs * 60
    return hrs, mins


class Boat:

    def __init__(self, name):
        self.nav = None
        self.wind = None
        self.heel = None
        self.pos = None
        self.sailplan = None
        self.sails = None
        self.name = name
        self.data = None
        self.datafile = os.path.join(DIR_SAILDATA, name + '_dat.json')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return 0

    def getdata(self, response_json=False, save=True):
        if not response_json:
            response_json = get_all_own_boats_json()
        for data in response_json:
            if data['boatname'] == self.name:
                self.data = data
        self.sails = [sail['sail'] for sail in self.data['sails']]
        self.sailplan = [sail['sail'] for sail in self.data['sails'] if sail['halyard'] == 1 and sail['furled'] == 0]
        self.pos = (round(self.data['latitude'], 5), round(self.data['longitude'], 5))
        self.heel = round(self.data['heeldegrees'], )
        self.wind = {'tws': round(self.data['tws'] * 2, 1),
                     'twa': round(self.data['twa']),
                     'twd': round(self.data['twd']),
                     'aws': round(self.data['aws'] * 2),
                     'awa': round(self.data['awa'])}
        self.nav = {'hdg': round(self.data['hdg']),
                    'spd': round(self.data['spd'] * 2, 1),
                    'cog': round(self.data['cog']),
                    'sog': round(self.data['sog'] * 2, 1),
                    'whlm': round(self.data['weatherhelm'], 2)
                    }
        if save:
            self.save_current_sail_data()
        return self.data

    def show_pos(self):
        print('lat: {}'.format(self.pos[0]))
        print('lon: {}'.format(self.pos[1]))

    def show_sailplan(self):
        for sail in self.sails:
            mark = ''
            if sail in self.sailplan:
                mark = 'X'
            print(sail.lower() + ':' + ' ' * (16 - len(sail)) + mark)

    def show_heel(self):
        print('heel: {}'.format(self.heel))

    def show_speed(self):
        print('tws: {}'.format(self.wind['tws']))
        print('spd: {}'.format(self.nav['spd']))
        print('sog: {}'.format(self.nav['sog']))

    def show_course(self):
        print('hdg: {}'.format(self.nav['hdg']))
        print('cog: {}'.format(self.nav['cog']))

    def __show_short__(self):
        self.show_pos()
        print('hdg: {}'.format(self.nav['hdg']))
        print('cog: {}'.format(self.nav['cog']))
        print('tws: {}'.format(self.wind['tws']))

    def __show_full__(self):
        self.show_pos()
        print('\n')
        self.show_sailplan()
        print('\n')
        for each in self.nav:
            print('{}: {}'.format(each, self.nav[each]))
        for each in self.wind:
            print('{}: {}'.format(each, self.wind[each]))
        self.show_heel()

    def show(self, full=False):
        print('{}\n----------------'.format(self.name.upper()))
        if full:
            self.__show_full__()
        else:
            self.__show_short__()

    def sail_config_snapshot(self):
        return {'tws': self.wind['tws'],
                'spd': self.nav['spd'],
                'twd': self.wind['twd'],
                'twa': self.wind['twa'],
                'heel': self.heel,
                'sails': self.sailplan}

    def __read_sail_data_from_file__(self):
        with open(self.datafile, 'r') as f:
            return json.load(f)

    def __write_sail_data_to_file__(self, dic):
        with open(self.datafile, 'w') as f:
            json.dump(dic, f)

    def save_current_sail_data(self):
        data = {}
        if os.path.exists(self.datafile):
            data = self.__read_sail_data_from_file__()
        data.update({str(time.time()): self.sail_config_snapshot()})
        self.__write_sail_data_to_file__(data)

    def get_sail_data(self):
        return pd.read_json(json.dumps(self.__read_sail_data_from_file__()), orient='index')


def get_arg(args, arg):
    for each in args:
        if arg in each:
            return each.split('=')[1]
