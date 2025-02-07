import os
from enum import Enum
from pathlib import Path

import keyring

# TODO Fix: all tests are broken

DIR_PROJ = Path(__file__).parent.parent.resolve()
DIR_HOME = Path(__file__).parent.resolve()
DIR_DATA = os.path.join(DIR_HOME, 'data')
DIR_MAPS = os.path.join(DIR_HOME, 'map')
DIR_LOGS = os.path.join(DIR_DATA, 'logs')
DIR_RACEMARKS = os.path.join(DIR_DATA, 'races')
DIR_ROUTE = os.path.join(DIR_HOME, 'route')
DIR_ROUTE_IN = os.path.join(DIR_ROUTE, 'in')
DIR_ROUTE_OUT = os.path.join(DIR_ROUTE, 'out')
DIR_ROUTE_TMP = os.path.join(DIR_ROUTE, 'tmp')
DIR_PKL = os.path.join(DIR_DATA, 'pkl')
DIR_TEST_FILES = os.path.join(DIR_DATA, 'test')

F_DESTINATIONS = os.path.join(DIR_DATA, 'destinations.csv')
F_TOML = os.path.join(DIR_PROJ, 'pyproject.toml')


class Maps(Enum):
    Windy = 1
    I_Boating = 2
    Folium = 3
    Open_Sea = 4


class datasource(Enum):
    remote = 0
    local = 1


URL_OPENSEA = 'https://map.openseamap.org/?zoom={}&lon={}&lat={}&layers=TFTFFFTFFTFFFFFFTFFFTF&mlat={}' \
              '&mlon={}&mtext={}'
URL_IBOATING = 'https://fishing-app.gpsnauticalcharts.com/i-boating-fishing-web-app/fishing-marine-charts' \
               '-navigation.html#{}/{}/{}'
URL_WINDY = 'https://www.windy.com/?{},{},{},m:eT5aeSC'

SAILS = [
    'Nr.1',
    'Nr.2',
    'Nr.3',
    'Stormjib',
    'Mainsail',
    'Genaker',
    'Mizzen',
    'Mizzen staysail'
]

POINTS_OF_SAIL = {
    'close haul': list(range(0, 37)),
    'close reach': list(range(36, 73)),
    'beam': list(range(72, 109)),
    'broad reach': list(range(108, 145)),
    'run': list(range(144, 181))
}

API_KEY = keyring.get_password('sailaway', 'api_key')
API_USER = keyring.get_password('sailaway', 'api_user')
API_OWN_BOATS = 'http://srv.sailaway.world/cgi-bin/sailaway/APIBoatInfo.pl?usrnr={}&key={}'.format(API_USER, API_KEY)
API_SIMULATED_RESPONSE_FILE = os.path.join(DIR_TEST_FILES, 'simulated.json')

DEFAULT_ZOOM = 7
DEFAULT_MAP = Maps.Folium
DEFAULT_UPDATE_INTERVAL = 600  # 10 min

DATETIME_FORMAT = '%d-%b %H:%M'

ALINGMENT_OFFEST = 12


class Thresholds:
    course = 1
    heel = 30
    tws = 30
    spd = 1  # min
    eta = 30  # days
