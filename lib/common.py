import requests
import os
from pathlib import Path
from datetime import datetime

MY_USER = 'Viper Vit'

DIR_HOME = str(Path.home())
DIR_ONSAIL = os.path.join(DIR_HOME, 'Documents', 'OnSail')
DIR_SAILDATA = os.path.join(DIR_ONSAIL, 'data')
DIR_HTML = DIR_ONSAIL

URL_RACES = 'https://sarl.ingenium.net.au/racelog?racenr='

RACE_IDS = {
    'Stardust': 38602,
    'The Ocean Race': 39147
}

API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr=59528&key' \
                '=7B79EE2988A44080A37C06570F4B5EE8'

URL_IBOATING_CHART = 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
                     '-navigation.html'


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
