import time
from datetime import datetime
from enum import Enum
import requests
import keyring

API_KEY = keyring.get_password('sailaway', 'api_key')
API_USER = keyring.get_password('sailaway', 'api_user')

API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr={}&key={}'.format(API_USER, API_KEY)

DEFAULT_ZOOM = 7


class Maps(Enum):
    Windy = 1
    I_Boating = 2
    Folium = 3
    Open_Sea = 4


DEFAULT_MAP = Maps.Folium


def get_all_own_boats_json():
    return requests.get(API_OWN_BOATS).json()


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


def ddm_to_dd(coors):
    semi = {'N': 1, 'S': -1, 'E': 1, 'W': -1}
    tmp1 = coors.split(' ')
    tmp2 = tmp1[0].split('°')
    return round((int(tmp2[0]) + float(tmp2[1]) / 60) * semi[tmp1[1]], 6)


def dd_to_dddm_single(coor, coortype=None):
    """type=0 for latitude, type=1 for longitude"""

    def add_zero(n):
        if n < 0:
            fill = 3
        else:
            fill = 2
        return str(n).zfill(fill)

    dd = int(coor)
    dm = abs(coor - dd) * 60
    mm = int(dm)
    dec = str(round(abs(dm - mm), 3)).split('.')[1]
    letter = None
    if coor >= 0 and coortype == 0:
        letter = 'N'
    if coor < 0 and coortype == 0:
        letter = 'S'
    if coor >= 0 and coortype == 1:
        letter = 'E'
    if coor < 0 and coortype == 1:
        letter = 'W'
    return '{}°{}.{} {}'.format(add_zero(abs(dd)), add_zero(mm), dec, letter)


def dd_to_ddm(coors):
    return '{}  {}'.format(dd_to_dddm_single(coors[0], 0), dd_to_dddm_single(coors[1], 1))


def calculate_eta(speed, distance):
    speed = float(speed)
    distance = float(distance)
    if speed != 0:
        total_hours = int(distance / speed)
        days = int(total_hours / 24)
        hours = total_hours - days * 24
        return '{}d {}h'.format(days, hours)
    else:
        return None


def miles_to_nautical(miles):
    return miles / 1.150779448


def seconds_to_formatted_output(secs):
    return time.strftime('%H:%M:%S', time.gmtime(secs))
