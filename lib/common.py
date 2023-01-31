from datetime import datetime

import requests

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


def get_arg(args, arg):
    for each in args:
        if arg in each:
            return each.split('=')[1]


def ddm_to_dd(coor):
    semi = {'N': 1, 'S': -1, 'E': 1, 'W': -1}
    tmp1 = coor.split(' ')
    tmp2 = tmp1[0].split('°')
    return round((int(tmp2[0]) + float(tmp2[1]) / 60) * semi[tmp1[1]], 6)
