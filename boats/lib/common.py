import json
import time
import tomllib
import warnings
from datetime import datetime

import pandas as pd
import requests
from geographiclib.geodesic import Geodesic
from geopy import distance

from boats import F_DESTINATIONS, API_OWN_BOATS, API_SIMULATED_RESPONSE_FILE, F_TOML


def get_version_from_pyproject(file_path=F_TOML):
    with open(file_path, "rb") as f:
        pyproject_data = tomllib.load(f)
        return pyproject_data.get("project", {}).get("version")


def get_all_own_boats_json():
    match not __debug__:  # the logic is inverted; to run  in debug mode '-O' must be used
        case True:
            warnings.warn('Running in debug mode!')
            with open(API_SIMULATED_RESPONSE_FILE, 'r') as f:
                return json.loads(f.read())
        case False:
            return requests.get(API_OWN_BOATS).json()


def make_log_file_name(boatname):
    return f'{boatname}.log'


def timestamp():
    return datetime.now().strftime('%d-%b-%Y %H:%M')


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


def get_destination_coordinates(name):
    df = pd.read_csv(F_DESTINATIONS)
    try:
        return df[df['Name'] == name][['Lat', 'Lon']].values[0].tolist()
    except IndexError:
        return False


def get_estimated_position(last_pos, hdg, spd, elapsed):
    '''Last pos - (lat, lon)
       hdg - degrees
       spd - knots
       elapsed - time since last position at speed=spd in hours
    '''
    d_est = spd * 1852 * elapsed
    gd = Geodesic.WGS84.Direct(last_pos[0], last_pos[1], hdg, d_est)
    return round(gd['lat2'], 2), round(gd['lon2'], 2)


def calc_course(start, dest):
    az = Geodesic.WGS84.Inverse(start[0], start[1], dest[0], dest[1])['azi1']
    if az < 0:
        az += 360
    return round(az)


def calc_total_voyage_distance(df_dist):
    total = 0
    for i in range(len(df_dist.index) - 1):
        prev = list(df_dist.iloc[i].values)
        curr = list(df_dist.iloc[i + 1].values)
        total += distance.distance(prev, curr).nm
    return round(total, )


def calc_total_voyage_days(ts_start, ts_end):
    return (ts_end - ts_start).days
